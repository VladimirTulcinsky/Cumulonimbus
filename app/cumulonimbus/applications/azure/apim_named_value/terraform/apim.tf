resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_resource_group" "lab" {
  name     = "${var.app_name}-${var.app_id}-${random_string.suffix.result}"
  location = "West Europe"

  tags = {
    app_id = var.app_id
  }
}

data "azuread_client_config" "current" {}

resource "azuread_application" "attacker" {
  display_name = "${var.app_name}-${var.app_id}-attacker-${random_string.suffix.result}"
}

resource "azuread_service_principal" "attacker" {
  client_id = azuread_application.attacker.client_id
}

resource "azuread_service_principal_password" "attacker" {
  service_principal_id = azuread_service_principal.attacker.id
}

resource "azurerm_role_assignment" "attacker_reader" {
  scope                = azurerm_resource_group.lab.id
  role_definition_name = "Reader"
  principal_id         = azuread_service_principal.attacker.id
}

resource "azurerm_api_management" "lab" {
  name                = "${var.app_name}-apim-${random_string.suffix.result}"
  location            = azurerm_resource_group.lab.location
  resource_group_name = azurerm_resource_group.lab.name
  publisher_name      = "Cumulonimbus Lab"
  publisher_email     = "lab@cumulonimbus.local"
  sku_name            = "Consumption_0"

  tags = {
    app_id = var.app_id
  }
}

resource "azurerm_api_management_named_value" "flag" {
  name                = "flag-key"
  resource_group_name = azurerm_resource_group.lab.name
  api_management_name = azurerm_api_management.lab.name
  display_name        = "flag-key"
  value               = "CUMULONIMBUS{AP1M_N4m3d_V4lu3_Pl41nt3xt}"
  secret              = false
}

resource "azurerm_api_management_named_value" "app_config" {
  name                = "app-config-endpoint"
  resource_group_name = azurerm_resource_group.lab.name
  api_management_name = azurerm_api_management.lab.name
  display_name        = "app-config-endpoint"
  value               = "https://config.cumulonimbus.local/api/v1"
  secret              = false
}
