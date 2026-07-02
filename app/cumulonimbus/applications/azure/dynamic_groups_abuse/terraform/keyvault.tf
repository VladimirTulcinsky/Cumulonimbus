resource "azurerm_key_vault" "flag" {
  name                      = "cumdga${random_integer.suffix.result}"
  location                  = azurerm_resource_group.rg.location
  resource_group_name       = azurerm_resource_group.rg.name
  tenant_id                 = var.tenant_id
  sku_name                  = "standard"
  enable_rbac_authorization = true
  purge_protection_enabled  = false
}

# Allow the deploying SP to create the secret
resource "azurerm_role_assignment" "tf_kv_admin" {
  scope                = azurerm_key_vault.flag.id
  role_definition_name = "Key Vault Administrator"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_key_vault_secret" "flag" {
  name         = "flag"
  value        = "CUMULONIMBUS{Dyn4m1c_Gr0up_M3mb3rsh1p_Abus3d}"
  key_vault_id = azurerm_key_vault.flag.id

  depends_on = [azurerm_role_assignment.tf_kv_admin]
}
