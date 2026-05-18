resource "azurerm_key_vault" "sqli_imds" {
  name                      = "kv-sqli-${random_id.suffix.hex}"
  location                  = azurerm_resource_group.sqli_imds.location
  resource_group_name       = azurerm_resource_group.sqli_imds.name
  tenant_id                 = data.azurerm_client_config.current.tenant_id
  sku_name                  = "standard"
  enable_rbac_authorization = true
  purge_protection_enabled  = false
}

# Deployer SP needs Secrets Officer to create the flag secret
resource "azurerm_role_assignment" "terraform_kv_secrets_officer" {
  scope                = azurerm_key_vault.sqli_imds.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "time_sleep" "kv_rbac_propagation" {
  depends_on      = [azurerm_role_assignment.terraform_kv_secrets_officer]
  create_duration = "30s"
}

resource "azurerm_key_vault_secret" "flag" {
  depends_on   = [time_sleep.kv_rbac_propagation]
  name         = "flag"
  value        = "CUMULONIMBUS{SQLi_IMDS_ManagedIdentityTokenExfil}"
  key_vault_id = azurerm_key_vault.sqli_imds.id
}

# VM managed identity gets Secrets User so it can read the flag via its token
resource "azurerm_role_assignment" "vm_kv_secrets_user" {
  scope                = azurerm_key_vault.sqli_imds.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_linux_virtual_machine.sqli_imds.identity[0].principal_id
}
