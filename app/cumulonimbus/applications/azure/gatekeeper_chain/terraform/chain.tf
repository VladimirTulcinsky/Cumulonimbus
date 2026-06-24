###############################################################################
# gatekeeper_chain — a flag-gated privilege-escalation ladder.
#
# The attacker starts with NO Azure access. A "gatekeeper" app (a container
# with a privileged managed identity) grants real RBAC when fed a correct flag:
#
#   public blob (flag0, anonymous)   --submit flag0--> Reader on the RG
#   RG tag       (flag1, Reader)     --submit flag1--> App Config Data Reader
#   App Config   (flag2, Data Reader)--submit flag2--> Storage Blob Data Reader
#   private blob (flag3, Blob Reader)--submit flag3--> Key Vault Secrets User
#   Key Vault    (FLAG, Secrets User)                 the CTFd flag
#
# Each unlock is a live role assignment created by the gatekeeper's managed
# identity (which holds User Access Administrator on the resource group).
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
  appconf_name = substr("cngk-conf-${local.base}", 0, 50)
  aci_name     = "cngk-gatekeeper-${random_id.suffix.hex}"
  kv_name      = substr("cngkkv${local.base}", 0, 24)
  kv_secret    = "app-flag"

  # Progression tokens (submitted to the gatekeeper). The final flag lives in
  # the Key Vault and is the one submitted to CTFd.
  flag0 = "CUMULONIMBUS{unlock_1_reader_access}"
  flag1 = "CUMULONIMBUS{unlock_2_appconfig_reader}"
  flag2 = "CUMULONIMBUS{unlock_3_blob_reader}"
  flag3 = "CUMULONIMBUS{unlock_4_keyvault_user}"

  # Built-in role definition IDs (stable GUIDs).
  role_reader  = "/subscriptions/${var.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/acdd72a7-3385-48ef-bd42-f606fba81ae7"
  role_appconf = "/subscriptions/${var.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/516239f1-63e1-4d78-a4de-a74fb236a071"
  role_blob    = "/subscriptions/${var.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/2a2b9908-6ea1-4ae2-8e65-a410df84e7d1"
  role_kv      = "/subscriptions/${var.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/4633458b-17de-408a-b874-0445c86b69e6"

  # flag -> what the gatekeeper grants the attacker on success.
  unlocks = {
    (local.flag0) = { label = "Reader on the resource group", scope = azurerm_resource_group.rg.id, roleDefinitionId = local.role_reader }
    (local.flag1) = { label = "App Configuration Data Reader", scope = azurerm_app_configuration.conf.id, roleDefinitionId = local.role_appconf }
    (local.flag2) = { label = "Storage Blob Data Reader", scope = azurerm_storage_account.sa.id, roleDefinitionId = local.role_blob }
    (local.flag3) = { label = "Key Vault Secrets User", scope = azurerm_key_vault.chain.id, roleDefinitionId = local.role_kv }
  }
}

resource "azurerm_resource_group" "rg" {
  name     = local.rg_name
  location = var.location

  # Stage 1 (needs Reader): the flag and a pointer to the App Configuration
  # store are recorded in resource-group tags.
  tags = {
    app_id          = var.app_id
    managed         = "terraform"
    "stage1-flag"   = local.flag1
    "config-store"  = local.appconf_name
    "stage1-note"   = "submit stage1-flag to the gatekeeper to unlock app configuration access"
  }

  depends_on = [
    azurerm_resource_provider_registration.microsoft_appconfiguration,
    azurerm_resource_provider_registration.microsoft_containerinstance,
  ]
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

# This is what lets the gatekeeper hand out roles. Creating it requires the
# DEPLOYER to be Owner (or User Access Administrator) on the subscription.
resource "azurerm_role_assignment" "gatekeeper_uaa" {
  scope                = azurerm_resource_group.rg.id
  role_definition_name = "User Access Administrator"
  principal_id         = azurerm_user_assigned_identity.gatekeeper.principal_id
}

###############################################################################
# Stage 0 — public blob with the first flag (no Azure auth required)
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

    Your first flag (submit it to the gatekeeper to gain Reader access):
      ${local.flag0}

    The gatekeeper URL is in your lab output. Submit a flag with:
      curl -s -X POST <gatekeeper-url>/unlock -H 'Content-Type: application/json' -d '{"flag":"<flag>"}'
  EOF
}

# Stage 4 — private blob (needs Storage Blob Data Reader) with flag3 + the
# coordinates of the Key Vault.
resource "azurerm_storage_container" "vault_notes" {
  name                  = "vault-notes"
  storage_account_name  = azurerm_storage_account.sa.name
  container_access_type = "private"
}

resource "azurerm_storage_blob" "vault_notes" {
  name                   = "notes.txt"
  storage_account_name   = azurerm_storage_account.sa.name
  storage_container_name = azurerm_storage_container.vault_notes.name
  type                   = "Block"
  source_content         = <<-EOF
    Key Vault access notes
    ----------------------
    Submit this flag to the gatekeeper to unlock Key Vault access:
      ${local.flag3}

    Then read the secret:
      Key Vault name : ${local.kv_name}
      Secret name    : ${local.kv_secret}
  EOF
}

###############################################################################
# Stage 2 — App Configuration (needs App Config Data Reader)
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

# The deployer needs data-plane access to write the key-values.
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

resource "azurerm_app_configuration_key" "stage2_flag" {
  configuration_store_id = azurerm_app_configuration.conf.id
  key                    = "secrets/next-unlock"
  value                  = local.flag2
  depends_on             = [time_sleep.appconf_rbac]
}

resource "azurerm_app_configuration_key" "stage2_note" {
  configuration_store_id = azurerm_app_configuration.conf.id
  key                    = "secrets/note"
  value                  = "Submit secrets/next-unlock to the gatekeeper to unlock blob access on storage account ${local.sa_name} (container vault-notes)."
  depends_on             = [time_sleep.appconf_rbac]
}

###############################################################################
# The gatekeeper — a container that grants RBAC in exchange for a correct flag.
# Runs python:3.12-slim, decodes app.py from a (secure) env var, installs deps,
# and serves on port 80. UNLOCKS_JSON and the app are SECURE env vars so the
# flags are never returned by `az container show`.
###############################################################################
resource "azurerm_container_group" "gatekeeper" {
  name                = local.aci_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  ip_address_type     = "Public"
  dns_name_label      = local.aci_name
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

  # The identity must hold User Access Administrator before it can grant roles.
  depends_on = [azurerm_role_assignment.gatekeeper_uaa]
}
