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
}

resource "azurerm_role_assignment" "terraform_kv_admin" {
  scope                = azurerm_key_vault.ska_kv.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "time_sleep" "kv_rbac_propagation" {
  depends_on      = [azurerm_role_assignment.terraform_kv_admin]
  create_duration = "30s"
}

resource "azurerm_key_vault_secret" "fapp-secret" {
  depends_on   = [time_sleep.kv_rbac_propagation]
  name         = "super-secret"
  value        = "CheckTheOtherSecrets1."
  key_vault_id = azurerm_key_vault.ska_kv.id
}

resource "azurerm_key_vault_secret" "flag" {
  depends_on   = [time_sleep.kv_rbac_propagation]
  name         = "flag"
  value        = "Cumulonimbus{SharedKeyAuthorizationShouldBeDisabled}."
  key_vault_id = azurerm_key_vault.ska_kv.id
}
