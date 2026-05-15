resource "random_id" "suffix" {
  byte_length = 4
}

locals {
  rg_name     = "cumulonimbus-${var.app_id}-${random_id.suffix.hex}"
  config_name = "cnimbus-config-${random_id.suffix.hex}"
}

resource "azurerm_resource_group" "rg" {
  name     = local.rg_name
  location = "West Europe"
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }

  depends_on = [azurerm_resource_provider_registration.microsoft_appconfiguration]
}

resource "azurerm_app_configuration" "config" {
  name                = local.config_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "free"

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# Store several key-values — the flag is one of them
resource "azurerm_app_configuration_key" "env" {
  configuration_store_id = azurerm_app_configuration.config.id
  key                    = "app/environment"
  value                  = "production"
}

resource "azurerm_app_configuration_key" "db_host" {
  configuration_store_id = azurerm_app_configuration.config.id
  key                    = "database/host"
  value                  = "prod-db.internal.example.com"
}

resource "azurerm_app_configuration_key" "db_password" {
  configuration_store_id = azurerm_app_configuration.config.id
  key                    = "database/password"
  value                  = "Pr0dDB!SuperSecure2024"
}

resource "azurerm_app_configuration_key" "api_key" {
  configuration_store_id = azurerm_app_configuration.config.id
  key                    = "secrets/api-key"
  value                  = "CUMULONIMBUS{App_C0nf1g_D4t4_R34d3r_Enum}"
}

# Attacker user with App Configuration Data Reader — can list and read all key-values
data "azuread_client_config" "current" {}

resource "azuread_user" "attacker" {
  user_principal_name   = "attacker-${random_id.suffix.hex}@${data.azuread_client_config.current.tenant_id}.onmicrosoft.com"
  display_name          = "Cumulonimbus Attacker ${random_id.suffix.hex}"
  password              = "C@ttack3r!${random_id.suffix.hex}"
  force_password_change = false
}

resource "azurerm_role_assignment" "attacker_data_reader" {
  scope                = azurerm_app_configuration.config.id
  role_definition_name = "App Configuration Data Reader"
  principal_id         = azuread_user.attacker.object_id
}
