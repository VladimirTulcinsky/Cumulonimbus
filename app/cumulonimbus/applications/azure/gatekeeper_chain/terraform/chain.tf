###############################################################################
# gatekeeper_chain — a flag-gated privilege-escalation ladder whose stages are
# the real "plaintext credential in an Azure resource" scenarios, merged into
# one lab. The attacker starts with NO access; a "gatekeeper" app grants a real
# Azure role (scoped to ONE resource at a time) in exchange for the previous
# stage's flag, so each unlock opens exactly the next scenario:
#
#   public blob   (bootstrap flag)        --submit--> Reader on the Container Instance
#   Container Instance env (Reader)       --submit--> Reader on the Data Factory
#   Data Factory linked service (Reader)  --submit--> App Configuration Data Reader
#   App Configuration (Data Reader)       --submit--> Reader on the Monitor action group
#   Monitor action group (Reader)         --submit--> Reader on the APIM service
#   APIM named value (Reader)             --submit--> Key Vault Secrets User
#   Key Vault secret (Secrets User)                  the CTFd flag
#
# Access is scoped per-resource (not RG-wide Reader) precisely because most of
# these scenarios are Reader-readable — without per-resource scoping a single
# Reader grant would expose every stage at once and defeat the ladder.
#
# APIM is deliberately the LAST scenario before the vault: it is the slowest
# resource to provision, so placing it late gives it the most time to be ready
# before a player reaches it.
###############################################################################

data "azuread_client_config" "current" {}
data "azurerm_client_config" "current" {}

resource "random_id" "suffix" {
  byte_length = 4
}

locals {
  suffix_alnum = lower(replace(var.name_suffix, "/[^a-zA-Z0-9]/", ""))
  base         = "${local.suffix_alnum}${random_id.suffix.hex}"

  rg_name      = "cumulonimbus-${var.app_id}-${random_id.suffix.hex}"
  sa_name      = substr("cngkch${local.base}", 0, 24)
  apim_name    = substr("cngk-apim-${local.base}", 0, 50)
  appconf_name = substr("cngk-conf-${local.base}", 0, 50)
  aci_app_name = "cngk-app-${random_id.suffix.hex}"
  adf_name     = substr("cngk-adf-${local.base}", 0, 63)
  ag_name      = "cngk-ag-${random_id.suffix.hex}"
  gk_name      = "cngk-gatekeeper-${random_id.suffix.hex}"
  kv_name      = substr("cngkkv${local.base}", 0, 24)
  kv_secret    = "app-flag"

  # Stage flags: the bootstrap token plus the *real* flags from the flat labs
  # this lab consolidates. The final flag lives in the Key Vault (the one
  # submitted to CTFd).
  flag_bootstrap = "CUMULONIMBUS{g4t3k33p3r_b00tstr4p}"
  flag_apim      = "CUMULONIMBUS{AP1M_N4m3d_V4lu3_Pl41nt3xt}"
  flag_appconfig = "CUMULONIMBUS{App_C0nf1g_D4t4_R34d3r_Enum}"
  flag_container = "CUMULONIMBUS{C0nt41n3r_1nst4nc3_Pl41nt3xt_Env}"
  flag_adf       = "CUMULONIMBUS{ADF_L1nk3d_S3rv1c3_Cl34rt3xt_K3y}"
  flag_monitor   = "CUMULONIMBUS{Monit0r_W3bh00k_T0k3n_3xp0s3d}"

  # Built-in role definition IDs (stable GUIDs).
  role_reader  = "/subscriptions/${var.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/acdd72a7-3385-48ef-bd42-f606fba81ae7"
  role_appconf = "/subscriptions/${var.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/516239f1-63e1-4d78-a4de-a74fb236a071"
  role_kv      = "/subscriptions/${var.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/4633458b-17de-408a-b874-0445c86b69e6"

  # flag -> what the gatekeeper grants the attacker (scoped to the NEXT resource).
  unlocks = {
    (local.flag_bootstrap) = { label = "Reader on the Container Instance", scope = azurerm_container_group.app.id, roleDefinitionId = local.role_reader }
    (local.flag_container) = { label = "Reader on the Data Factory", scope = azurerm_data_factory.adf.id, roleDefinitionId = local.role_reader }
    (local.flag_adf)       = { label = "App Configuration Data Reader", scope = azurerm_app_configuration.conf.id, roleDefinitionId = local.role_appconf }
    (local.flag_appconfig) = { label = "Reader on the Monitor action group", scope = azurerm_monitor_action_group.ag.id, roleDefinitionId = local.role_reader }
    (local.flag_monitor)   = { label = "Reader on the APIM service", scope = azurerm_api_management.apim.id, roleDefinitionId = local.role_reader }
    (local.flag_apim)      = { label = "Key Vault Secrets User", scope = azurerm_key_vault.chain.id, roleDefinitionId = local.role_kv }
  }
}

resource "azurerm_resource_group" "rg" {
  name     = local.rg_name
  location = var.location

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# ── Attacker user — starts with NO role assignments at all ───────────────────
resource "azuread_user" "attacker" {
  user_principal_name   = "attacker-${random_id.suffix.hex}@${var.tenant_domain}"
  display_name          = "Cumulonimbus Attacker ${random_id.suffix.hex}"
  password              = "C@ttack3r!${random_id.suffix.hex}"
  force_password_change = false
}

# ── Gatekeeper managed identity (User Access Administrator on the RG) ─────────
resource "azurerm_user_assigned_identity" "gatekeeper" {
  name                = "cngk-gatekeeper-mi-${random_id.suffix.hex}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
}

# What lets the gatekeeper hand out roles. Creating it requires the DEPLOYER to
# be Owner (or User Access Administrator) on the subscription.
resource "azurerm_role_assignment" "gatekeeper_uaa" {
  scope                = azurerm_resource_group.rg.id
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

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
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
    Cumulonimbus — Gatekeeper Challenge

    Resource group : ${local.rg_name}

    Your bootstrap flag (submit it to the gatekeeper to gain Reader on the
    Container Instance "${local.aci_app_name}"):
      ${local.flag_bootstrap}

    Submit a flag:
      curl -s -X POST <gatekeeper-url>/unlock -H 'Content-Type: application/json' -d '{"flag":"<flag>"}'

    Then log in as the attacker and read the next stage. Each stage's value is
    the flag that unlocks the following one.
  EOF
}

###############################################################################
# Stage 1 — APIM named value (Reader on the APIM service)
###############################################################################
resource "azurerm_api_management" "apim" {
  name                = local.apim_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  publisher_name      = "Cumulonimbus Lab"
  publisher_email     = "lab@cumulonimbus.local"
  sku_name            = "Consumption_0"

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "azurerm_api_management_named_value" "flag" {
  name                = "flag-key"
  resource_group_name = azurerm_resource_group.rg.name
  api_management_name = azurerm_api_management.apim.name
  display_name        = "flag-key"
  value               = local.flag_apim
  secret              = false
}

resource "azurerm_api_management_named_value" "next_hop" {
  name                = "next-hop"
  resource_group_name = azurerm_resource_group.rg.name
  api_management_name = azurerm_api_management.apim.name
  display_name        = "next-hop"
  value               = "Submit flag-key to the gatekeeper, then read Key Vault ${local.kv_name} secret ${local.kv_secret}."
  secret              = false
}

###############################################################################
# Stage 2 — App Configuration (App Configuration Data Reader)
###############################################################################
resource "azurerm_app_configuration" "conf" {
  name                = local.appconf_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  # "standard": the free tier allows only one store per subscription.
  sku = "standard"

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "azurerm_role_assignment" "deployer_appconf_owner" {
  scope                = azurerm_app_configuration.conf.id
  role_definition_name = "App Configuration Data Owner"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "time_sleep" "appconf_rbac" {
  depends_on      = [azurerm_role_assignment.deployer_appconf_owner]
  create_duration = "30s"
}

resource "azurerm_app_configuration_key" "env" {
  configuration_store_id = azurerm_app_configuration.conf.id
  key                    = "app/environment"
  value                  = "production"
  depends_on             = [time_sleep.appconf_rbac]
}

resource "azurerm_app_configuration_key" "flag" {
  configuration_store_id = azurerm_app_configuration.conf.id
  key                    = "secrets/api-key"
  value                  = local.flag_appconfig
  depends_on             = [time_sleep.appconf_rbac]
}

resource "azurerm_app_configuration_key" "next_hop" {
  configuration_store_id = azurerm_app_configuration.conf.id
  key                    = "secrets/next-hop"
  value                  = "Submit secrets/api-key to the gatekeeper, then read the Monitor action group ${local.ag_name}."
  depends_on             = [time_sleep.appconf_rbac]
}

###############################################################################
# Stage 3 — Container Instance plaintext env vars (Reader on the container)
###############################################################################
resource "azurerm_container_group" "app" {
  name                = local.aci_app_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  ip_address_type     = "None"
  os_type             = "Linux"
  restart_policy      = "Never"

  container {
    name   = "app"
    image  = "alpine:3.18"
    cpu    = "0.5"
    memory = "0.5"

    commands = ["sh", "-c", "echo Starting application && sleep 3600"]

    environment_variables = {
      "APP_VERSION" = "2.4.1"
      "ENVIRONMENT" = "production"
      "SECRET_FLAG" = local.flag_container
      "NEXT_HOP"    = "Submit SECRET_FLAG to the gatekeeper, then read Data Factory ${local.adf_name} linked service DataLakeConnection."
    }

    secure_environment_variables = {}

    ports {
      port     = 8080
      protocol = "TCP"
    }
  }

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

###############################################################################
# Stage 4 — Data Factory linked service cleartext key (Reader on the factory)
###############################################################################
resource "azurerm_data_factory" "adf" {
  name                = local.adf_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "azurerm_data_factory_linked_service_azure_blob_storage" "data" {
  name              = "DataLakeConnection"
  data_factory_id   = azurerm_data_factory.adf.id
  description       = "Primary data lake connection. Next: submit the AccountKey to the gatekeeper, then enumerate App Configuration store ${local.appconf_name}."
  connection_string = "DefaultEndpointsProtocol=https;AccountName=cumulonimbusdata;AccountKey=${local.flag_adf};EndpointSuffix=core.windows.net"
}

###############################################################################
# Stage 5 — Monitor action group webhook token (Reader on the action group)
###############################################################################
resource "azurerm_monitor_action_group" "ag" {
  name                = local.ag_name
  resource_group_name = azurerm_resource_group.rg.name
  short_name          = "cnimbus"

  webhook_receiver {
    name        = "security-alerts"
    service_uri = "https://webhook.cumulonimbus.local/alerts?token=${local.flag_monitor}"
  }

  webhook_receiver {
    name        = "apim-pointer"
    service_uri = "https://notes.cumulonimbus.local/?next=apim&service=${local.apim_name}&namedValue=flag-key"
  }

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

###############################################################################
# The gatekeeper — a container that grants RBAC in exchange for a correct flag.
# python:3.12-slim, app injected via a SECURE env var (flags never returned by
# the control plane), serves on port 80.
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
    image  = "python:3.12-slim"
    cpu    = "1.0"
    memory = "1.5"

    commands = [
      "sh", "-c",
      "echo \"$APP_B64\" | base64 -d > /app.py && pip install --quiet --no-cache-dir flask requests azure-identity && python /app.py",
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

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }

  depends_on = [azurerm_role_assignment.gatekeeper_uaa]
}
