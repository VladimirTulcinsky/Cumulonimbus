resource "random_integer" "exposed_app_registration" {
  min = 1
  max = 999999
}

data "azuread_client_config" "current" {}

# ── App Registration with a client secret ─────────────────────────────────────

resource "azuread_application" "portal" {
  display_name = "cumulonimbus-portal-${random_integer.exposed_app_registration.result}"
}

resource "azuread_service_principal" "portal" {
  client_id = azuread_application.portal.client_id
}

resource "azuread_application_password" "portal" {
  application_id = azuread_application.portal.id
  display_name   = "portal-client-secret"
  end_date       = "2030-01-01T00:00:00Z"
}

# ── Private flag storage ──────────────────────────────────────────────────────

resource "azurerm_resource_group" "exposed_app_registration" {
  name     = "exposed-app-reg-lab"
  location = "West Europe"
}

resource "azurerm_storage_account" "flag" {
  name                     = "cmlnmbsappreg${random_integer.exposed_app_registration.result}"
  resource_group_name      = azurerm_resource_group.exposed_app_registration.name
  location                 = azurerm_resource_group.exposed_app_registration.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "secrets" {
  name                  = "secrets"
  storage_account_name  = azurerm_storage_account.flag.name
  container_access_type = "private"
}

resource "azurerm_storage_blob" "flag" {
  name                   = "flag.txt"
  storage_account_name   = azurerm_storage_account.flag.name
  storage_container_name = azurerm_storage_container.secrets.name
  type                   = "Block"
  source_content         = "CUMULONIMBUS{3xp0s3d_4pp_R3g_Cl13nt_S3cr3t}\n"
}

# Grant the service principal Storage Blob Data Reader on the flag storage
resource "azurerm_role_assignment" "portal_sp_reader" {
  scope                = azurerm_storage_account.flag.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = azuread_service_principal.portal.object_id
}

# ── Public storage with the exposed config.json ───────────────────────────────
# Misconfiguration: a developer committed application config — including the
# app registration client secret — to a public storage blob "for convenience".

resource "azurerm_storage_account" "config" {
  name                     = "cmlnmbscfg${random_integer.exposed_app_registration.result}"
  resource_group_name      = azurerm_resource_group.exposed_app_registration.name
  location                 = azurerm_resource_group.exposed_app_registration.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "public_config" {
  name                  = "config"
  storage_account_name  = azurerm_storage_account.config.name
  container_access_type = "blob"
}

resource "azurerm_storage_blob" "app_config" {
  name                   = "config.json"
  storage_account_name   = azurerm_storage_account.config.name
  storage_container_name = azurerm_storage_container.public_config.name
  type                   = "Block"
  content_type           = "application/json"

  source_content = jsonencode({
    application = "cumulonimbus-portal"
    environment = "production"
    azure = {
      tenant_id     = data.azuread_client_config.current.tenant_id
      client_id     = azuread_application.portal.client_id
      # Misconfiguration: client secret embedded in a public config file
      client_secret = azuread_application_password.portal.value
    }
    storage = {
      account_name   = azurerm_storage_account.flag.name
      container_name = "secrets"
    }
  })
}
