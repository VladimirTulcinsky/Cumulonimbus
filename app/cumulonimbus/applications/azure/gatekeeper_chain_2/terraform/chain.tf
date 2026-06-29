###############################################################################
# gatekeeper_chain_2 — a flag-gated privilege-escalation ladder over a SECOND
# set of "plaintext credential in an Azure resource" scenarios (companion to
# gatekeeper_chain). The attacker starts with NO access; a "gatekeeper" app
# grants a real Azure role (scoped to ONE resource at a time) in exchange for
# the previous stage's flag:
#
#   public blob (bootstrap)              --submit--> Reader on the tags RG
#   resource-group tags (Reader)         --submit--> Reader on the deployment RG
#   ARM deployment history (Reader)      --submit--> Reader on the policy RG
#   policy assignment metadata (Reader)  --submit--> Reader on the Container App
#   Container App env (Reader)           --submit--> Reader on the Logic App
#   Logic App workflow (Reader)          --submit--> Reader on the Deployment Script
#   Deployment Script output (Reader)    --submit--> Website Contributor on the App Service
#   App Service app settings (Website Contributor) --submit--> Reader on the Event Grid topic
#   Event Grid topic tags (Reader)                 --submit--> Key Vault Secrets User
#   Key Vault secret (Secrets User)                the CTFd flag
#
# Three scenarios are resource-group-level (tags, deployment history, policy), so
# each gets its OWN resource group to keep stages isolated. One needs a non-Reader
# role: App Service app settings (Website Contributor, for the config/list action).
###############################################################################

data "azuread_client_config" "current" {}
data "azurerm_client_config" "current" {}

# Built-in policy definition reused by the policy-metadata scenario.
data "azurerm_policy_definition" "audit_unmanaged_disks" {
  name = "06a78e20-9358-41c9-923c-fb736d382a4d"
}

resource "random_id" "suffix" {
  byte_length = 4
}

# Idempotently register the resource providers this lab needs. `az provider
# register` is a no-op when a provider is already registered, so this works on
# both fresh subscriptions (where e.g. Microsoft.App is missing) and ones that
# already have everything — unlike azurerm_resource_provider_registration, which
# errors when the provider already exists. Every resource group depends on this.
resource "null_resource" "register_providers" {
  triggers = {
    subscription = var.subscription_id
  }

  provisioner "local-exec" {
    interpreter = ["/bin/sh", "-c"]
    environment = {
      AZ_CLIENT_ID       = var.client_id
      AZ_CLIENT_SECRET   = var.client_secret
      AZ_TENANT_ID       = var.tenant_id
      AZ_SUBSCRIPTION_ID = var.subscription_id
    }
    command = <<-EOT
      set -eu
      AZURE_CONFIG_DIR="$(mktemp -d)"
      export AZURE_CONFIG_DIR
      az login --service-principal -u "$AZ_CLIENT_ID" -p "$AZ_CLIENT_SECRET" --tenant "$AZ_TENANT_ID" >/dev/null
      if [ -n "$AZ_SUBSCRIPTION_ID" ]; then
        az account set --subscription "$AZ_SUBSCRIPTION_ID"
      fi
      for ns in Microsoft.App Microsoft.OperationalInsights Microsoft.EventGrid \
                Microsoft.Logic Microsoft.Web Microsoft.ManagedIdentity \
                Microsoft.KeyVault Microsoft.Storage; do
        az provider register --namespace "$ns" --wait
      done
      az logout >/dev/null 2>&1 || true
    EOT
  }
}

locals {
  suffix_alnum = lower(replace(var.name_suffix, "/[^a-zA-Z0-9]/", ""))
  base         = "${local.suffix_alnum}${random_id.suffix.hex}"

  rg_name        = "cumulonimbus-${var.app_id}-${random_id.suffix.hex}"
  rg_tags_name   = "cumulonimbus-${var.app_id}-tags-${random_id.suffix.hex}"
  rg_deploy_name = "cumulonimbus-${var.app_id}-deploy-${random_id.suffix.hex}"
  rg_policy_name = "cumulonimbus-${var.app_id}-policy-${random_id.suffix.hex}"

  sa_name       = substr("cngk2${local.base}", 0, 24)
  law_name      = "cngk2-law-${random_id.suffix.hex}"
  cae_name      = "cngk2-cae-${random_id.suffix.hex}"
  ca_name       = "cngk2-ca-${random_id.suffix.hex}"
  logic_name    = "cngk2-logic-${random_id.suffix.hex}"
  ds_uai_name   = "cngk2-ds-id-${random_id.suffix.hex}"
  ds_name       = "cngk2-script-${random_id.suffix.hex}"
  plan_name     = "cngk2-plan-${random_id.suffix.hex}"
  app_name      = "cngk2-app-${random_id.suffix.hex}"
  eg_topic_name = "cngk2-topic-${random_id.suffix.hex}"
  gk_name       = "cngk2-gatekeeper-${random_id.suffix.hex}"
  kv_name       = substr("cngk2kv${local.base}", 0, 24)
  kv_secret     = "app-flag"

  # Stage flags reused verbatim from the standalone labs. The final flag lives in
  # the Key Vault (the one submitted to CTFd).
  flag_bootstrap    = "CUMULONIMBUS{g4t3k33p3r2_b00tstr4p}"
  flag_tags         = "CUMULONIMBUS{S3cr3t_1n_R3s0urc3_Gr0up_T4gs}"
  flag_arm          = "CUMULONIMBUS{4RM_D3pl0yment_H1st0ry_Pl41nt3xt}"
  flag_policy       = "CUMULONIMBUS{P0l1cy_M3t4d4t4_S3cr3t_3xp0s3d}"
  flag_containerapp = "CUMULONIMBUS{C0nt41n3r_App_Env_V4rs_3xp0s3d}"
  flag_logic        = "CUMULONIMBUS{L0g1c_App_H4rdcod3d_Cr3d3nt14ls}"
  flag_script       = "CUMULONIMBUS{D3pl0ym3nt_Scr1pt_0utput_3xp0s3d}"
  flag_appservice   = "CUMULONIMBUS{App_S3rv1c3_Env_V4rs_3xp0s3d}"
  flag_eventgrid    = "CUMULONIMBUS{3v3ntGr1d_W3bh00k_T0k3n_3xp0s3d}"

  # Built-in role definition GUIDs.
  role_reader  = "acdd72a7-3385-48ef-bd42-f606fba81ae7"
  role_website = "de139f84-1756-47ae-9be6-808fbbe84772" # Website Contributor (app settings list)
  role_kv      = "4633458b-17de-408a-b874-0445c86b69e6" # Key Vault Secrets User

  # flag -> what the gatekeeper grants the attacker (scoped to the NEXT resource).
  unlocks = {
    (local.flag_bootstrap)    = { label = "Reader on the tags resource group", scope = azurerm_resource_group.tags.id, roles = [local.role_reader] }
    (local.flag_tags)         = { label = "Reader on the deployment resource group", scope = azurerm_resource_group.deploy.id, roles = [local.role_reader] }
    (local.flag_arm)          = { label = "Reader on the policy resource group", scope = azurerm_resource_group.policy.id, roles = [local.role_reader] }
    (local.flag_policy)       = { label = "Reader on the Container App", scope = azurerm_container_app.app.id, roles = [local.role_reader] }
    (local.flag_containerapp) = { label = "Reader on the Logic App", scope = azurerm_logic_app_workflow.app.id, roles = [local.role_reader] }
    (local.flag_logic)        = { label = "Reader on the Deployment Script", scope = azurerm_resource_deployment_script_azure_cli.app.id, roles = [local.role_reader] }
    (local.flag_script)       = { label = "Website Contributor on the App Service", scope = azurerm_linux_web_app.app.id, roles = [local.role_website] }
    (local.flag_appservice)   = { label = "Reader on the Event Grid topic", scope = azurerm_eventgrid_topic.app.id, roles = [local.role_reader] }
    (local.flag_eventgrid)    = { label = "Key Vault Secrets User", scope = azurerm_key_vault.chain.id, roles = [local.role_kv] }
  }
}

###############################################################################
# Resource groups: one main RG for the resource-scoped scenarios, plus three
# dedicated RGs for the resource-group-level scenarios (so each stays isolated).
###############################################################################
resource "azurerm_resource_group" "rg" {
  name       = local.rg_name
  location   = var.location
  tags       = { app_id = var.app_id, managed = "terraform" }
  depends_on = [null_resource.register_providers]
}

resource "azurerm_resource_group" "deploy" {
  name       = local.rg_deploy_name
  location   = var.location
  tags       = { app_id = var.app_id, managed = "terraform" }
  depends_on = [null_resource.register_providers]
}

resource "azurerm_resource_group" "policy" {
  name       = local.rg_policy_name
  location   = var.location
  tags       = { app_id = var.app_id, managed = "terraform" }
  depends_on = [null_resource.register_providers]
}

# Stage 1 — resource-group tags. The secret (and the pointer to the next stage)
# live in this RG's tags; a Reader can read them.
resource "azurerm_resource_group" "tags" {
  name       = local.rg_tags_name
  location   = var.location
  depends_on = [null_resource.register_providers]
  tags = {
    app_id         = var.app_id
    managed        = "terraform"
    "deploy-token" = local.flag_tags
    "next-hop"     = "Submit deploy-token to the gatekeeper, then read deployment history in resource group ${local.rg_deploy_name}."
  }
}

###############################################################################
# Attacker + gatekeeper identity (User Access Administrator on every RG it
# hands out roles in: the main RG and the three dedicated RGs).
###############################################################################
resource "azuread_user" "attacker" {
  user_principal_name   = "attacker2-${random_id.suffix.hex}@${var.tenant_domain}"
  display_name          = "Cumulonimbus Attacker2 ${random_id.suffix.hex}"
  password              = "C@ttack3r!${random_id.suffix.hex}"
  force_password_change = false
}

resource "azurerm_user_assigned_identity" "gatekeeper" {
  name                = "cngk2-gatekeeper-mi-${random_id.suffix.hex}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
}

resource "azurerm_role_assignment" "gatekeeper_uaa_main" {
  scope                = azurerm_resource_group.rg.id
  role_definition_name = "User Access Administrator"
  principal_id         = azurerm_user_assigned_identity.gatekeeper.principal_id
}

resource "azurerm_role_assignment" "gatekeeper_uaa_tags" {
  scope                = azurerm_resource_group.tags.id
  role_definition_name = "User Access Administrator"
  principal_id         = azurerm_user_assigned_identity.gatekeeper.principal_id
}

resource "azurerm_role_assignment" "gatekeeper_uaa_deploy" {
  scope                = azurerm_resource_group.deploy.id
  role_definition_name = "User Access Administrator"
  principal_id         = azurerm_user_assigned_identity.gatekeeper.principal_id
}

resource "azurerm_role_assignment" "gatekeeper_uaa_policy" {
  scope                = azurerm_resource_group.policy.id
  role_definition_name = "User Access Administrator"
  principal_id         = azurerm_user_assigned_identity.gatekeeper.principal_id
}

###############################################################################
# Bootstrap — public blob with the first flag (no Azure auth required)
###############################################################################
resource "azurerm_storage_account" "sa" {
  name                            = local.sa_name
  resource_group_name             = azurerm_resource_group.rg.name
  location                        = azurerm_resource_group.rg.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  allow_nested_items_to_be_public = true
  tags                            = { app_id = var.app_id, managed = "terraform" }
}

resource "azurerm_storage_container" "public" {
  name                  = "public"
  storage_account_name  = azurerm_storage_account.sa.name
  container_access_type = "blob"
}

resource "azurerm_storage_blob" "welcome" {
  name                   = "welcome.txt"
  storage_account_name   = azurerm_storage_account.sa.name
  storage_container_name = azurerm_storage_container.public.name
  type                   = "Block"
  source_content         = <<-EOF
    Cumulonimbus — Gatekeeper Challenge (part 2)

    Your bootstrap flag (submit it to the gatekeeper to gain Reader on the
    resource group "${local.rg_tags_name}"):
      ${local.flag_bootstrap}

    Submit a flag:
      curl -s -X POST <gatekeeper-url>/unlock -H 'Content-Type: application/json' -d '{"flag":"<flag>"}'

    Then log in as the attacker and read the next stage. Each stage's value is
    the flag that unlocks the following one.
  EOF
}

###############################################################################
# Stage 2 — ARM deployment history (plaintext string parameter)
###############################################################################
resource "azurerm_resource_group_template_deployment" "arm" {
  name                = "app-infra-v1"
  resource_group_name = azurerm_resource_group.deploy.name
  deployment_mode     = "Incremental"

  parameters_content = jsonencode({
    adminApiKey = { value = local.flag_arm }
    environment = { value = "production" }
    nextHop     = { value = "Submit adminApiKey to the gatekeeper, then read the policy assignment in resource group ${local.rg_policy_name}." }
  })

  template_content = jsonencode({
    "$schema"      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#"
    contentVersion = "1.0.0.0"
    parameters = {
      adminApiKey = { type = "string", metadata = { description = "Admin API key" } }
      environment = { type = "string" }
      nextHop     = { type = "string" }
    }
    resources = []
    outputs   = {}
  })
}

###############################################################################
# Stage 3 — policy assignment metadata
###############################################################################
resource "azurerm_resource_group_policy_assignment" "policy" {
  name                 = "cngk2-${random_id.suffix.hex}"
  resource_group_id    = azurerm_resource_group.policy.id
  policy_definition_id = data.azurerm_policy_definition.audit_unmanaged_disks.id
  display_name         = "Cumulonimbus Lab Policy"
  description          = "Audit VMs not using managed disks"

  metadata = jsonencode({
    "internal-token" = local.flag_policy
    "environment"    = "training"
    "next-hop"       = "Submit internal-token to the gatekeeper, then read the Container App ${local.ca_name}."
  })
}

###############################################################################
# Stage 4 — Container App env vars
###############################################################################
resource "azurerm_log_analytics_workspace" "law" {
  name                = local.law_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = { app_id = var.app_id }
}

resource "azurerm_container_app_environment" "cae" {
  name                       = local.cae_name
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
  tags                       = { app_id = var.app_id }
}

resource "azurerm_container_app" "app" {
  name                         = local.ca_name
  container_app_environment_id = azurerm_container_app_environment.cae.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {
    container {
      name   = "app"
      image  = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name  = "APP_ENV"
        value = "production"
      }
      env {
        name  = "SECRET_FLAG"
        value = local.flag_containerapp
      }
      env {
        name  = "NEXT_HOP"
        value = "Submit SECRET_FLAG to the gatekeeper, then read the Logic App ${local.logic_name}."
      }
    }
  }

  tags = { app_id = var.app_id }
}

###############################################################################
# Stage 5 — Logic App workflow (hardcoded credentials in an HTTP action)
###############################################################################
resource "azurerm_logic_app_workflow" "app" {
  name                = local.logic_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  tags                = { app_id = var.app_id }
}

resource "azurerm_logic_app_trigger_recurrence" "hourly" {
  name         = "Recurrence"
  logic_app_id = azurerm_logic_app_workflow.app.id
  frequency    = "Hour"
  interval     = 1
}

resource "azurerm_logic_app_action_http" "notify" {
  name         = "Notify-Backend"
  logic_app_id = azurerm_logic_app_workflow.app.id
  method       = "POST"
  uri          = "https://api.internal.example.com/notify"

  headers = {
    "Content-Type"  = "application/json"
    "Authorization" = "Bearer ${local.flag_logic}"
  }

  body = jsonencode({
    event   = "hourly_sync"
    nextHop = "Submit the Authorization bearer token to the gatekeeper, then read the Deployment Script ${local.ds_name}."
  })
}

###############################################################################
# Stage 6 — Deployment Script (secret in the script output)
###############################################################################
resource "azurerm_user_assigned_identity" "script" {
  name                = local.ds_uai_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
}

resource "azurerm_role_assignment" "script_contributor" {
  scope                = azurerm_resource_group.rg.id
  role_definition_name = "Contributor"
  principal_id         = azurerm_user_assigned_identity.script.principal_id
}

resource "azurerm_resource_deployment_script_azure_cli" "app" {
  name                = local.ds_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  version             = "2.40.0"
  retention_interval  = "P1D"
  cleanup_preference  = "OnExpiration"

  script_content = "echo '{\"flag\":\"${local.flag_script}\",\"nextHop\":\"Submit flag to the gatekeeper, then read App Service ${local.app_name} settings.\"}' > $AZ_SCRIPTS_OUTPUT_PATH"

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.script.id]
  }

  depends_on = [azurerm_role_assignment.script_contributor]
  tags       = { app_id = var.app_id }
}

###############################################################################
# Stage 7 — App Service app settings (need Website Contributor to list)
###############################################################################
resource "azurerm_service_plan" "plan" {
  name                = local.plan_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "B1"
  tags                = { app_id = var.app_id }
}

resource "azurerm_linux_web_app" "app" {
  name                = local.app_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.plan.id

  site_config {
    application_stack {
      python_version = "3.11"
    }
  }

  app_settings = {
    "ENVIRONMENT" = "production"
    "SECRET_FLAG" = local.flag_appservice
    "NEXT_HOP"    = "Submit SECRET_FLAG to the gatekeeper, then read the Event Grid topic ${local.eg_topic_name}."
  }

  tags = { app_id = var.app_id }
}

###############################################################################
# Stage 8 — Event Grid webhook token (full URL needs getFullUrl)
###############################################################################
resource "azurerm_eventgrid_topic" "app" {
  name                = local.eg_topic_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  # Event Grid performs a mandatory ownership handshake on custom webhook URLs,
  # so a fake endpoint cannot be attached as a real event subscription (creation
  # fails endpoint validation). The "configured" webhook URL — with its embedded
  # auth token — is instead recorded in the topic's tags, readable by any Reader.
  tags = {
    app_id        = var.app_id
    managed       = "terraform"
    "webhook-url" = "https://hooks.internal.example.com/events?token=${local.flag_eventgrid}&source=azure"
    "next-hop"    = "Submit the token from webhook-url to the gatekeeper, then read Key Vault ${local.kv_name} secret ${local.kv_secret}."
  }
}

###############################################################################
# The gatekeeper — grants RBAC in exchange for a correct flag (stdlib HTTP
# server + managed-identity token + ARM REST; see gatekeeper/app.py).
###############################################################################
resource "azurerm_container_group" "gatekeeper" {
  name                = local.gk_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  ip_address_type     = "Public"
  dns_name_label      = local.gk_name
  restart_policy      = "Always"

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.gatekeeper.id]
  }

  container {
    name   = "gatekeeper"
    image  = "mcr.microsoft.com/azure-cli:latest"
    cpu    = "1.0"
    memory = "1.5"

    commands = [
      "sh", "-c",
      "echo \"$APP_B64\" | base64 -d > /app.py && python3 /app.py",
    ]

    ports {
      port     = 80
      protocol = "TCP"
    }

    environment_variables = {
      "MI_CLIENT_ID"          = azurerm_user_assigned_identity.gatekeeper.client_id
      "ATTACKER_PRINCIPAL_ID" = azuread_user.attacker.object_id
    }

    secure_environment_variables = {
      "APP_B64"      = base64encode(file("${path.module}/gatekeeper/app.py"))
      "UNLOCKS_JSON" = jsonencode(local.unlocks)
    }
  }

  tags = { app_id = var.app_id, managed = "terraform" }

  depends_on = [
    azurerm_role_assignment.gatekeeper_uaa_main,
    azurerm_role_assignment.gatekeeper_uaa_tags,
    azurerm_role_assignment.gatekeeper_uaa_deploy,
    azurerm_role_assignment.gatekeeper_uaa_policy,
  ]
}
