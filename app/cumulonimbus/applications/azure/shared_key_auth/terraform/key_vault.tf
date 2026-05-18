data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "ska_kv" {
  name     = "ska-kv-rg"
  location = "West Europe"
}

resource "azurerm_key_vault" "ska_kv" {
  name                      = "kvska${var.app_name}${random_integer.ska.result}"
  location                  = azurerm_resource_group.ska_kv.location
  resource_group_name       = azurerm_resource_group.ska_kv.name
  tenant_id                 = data.azurerm_client_config.current.tenant_id
  sku_name                  = "standard"
  enable_rbac_authorization = true

  /*   network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
    ip_rules       = [var.attacker_public_ip]
  } */
}


resource "azurerm_key_vault_secret" "fapp-secret" {
  name         = "super-secret"
  value        = "CheckTheOtherSecrets1."
  key_vault_id = azurerm_key_vault.ska_kv.id
}

resource "azurerm_key_vault_secret" "flag" {
  name         = "flag"
  value        = "Cumulonimbus{SharedKeyAuthorizationShouldBeDisabled}."
  key_vault_id = azurerm_key_vault.ska_kv.id
}
