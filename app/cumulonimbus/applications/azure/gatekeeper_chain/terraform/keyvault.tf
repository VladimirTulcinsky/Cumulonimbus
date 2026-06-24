###############################################################################
# Final stage — Key Vault holding the flag. The attacker only reaches it after
# the gatekeeper grants "Key Vault Secrets User" in exchange for the previous
# stage's flag.
###############################################################################
resource "azurerm_key_vault" "chain" {
  name                      = local.kv_name
  location                  = azurerm_resource_group.rg.location
  resource_group_name       = azurerm_resource_group.rg.name
  tenant_id                 = data.azurerm_client_config.current.tenant_id
  sku_name                  = "standard"
  enable_rbac_authorization = true
  purge_protection_enabled  = false
}

# The deployer (the credentials running Terraform) needs write access to seed
# the secret.
resource "azurerm_role_assignment" "deployer_kv_officer" {
  scope                = azurerm_key_vault.chain.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "time_sleep" "kv_rbac_propagation" {
  depends_on      = [azurerm_role_assignment.deployer_kv_officer]
  create_duration = "30s"
}

resource "azurerm_key_vault_secret" "flag" {
  depends_on   = [time_sleep.kv_rbac_propagation]
  name         = local.kv_secret
  value        = "CUMULONIMBUS{G4t3k33p3r_RBAC_Pr1v3sc_Ch41n}"
  key_vault_id = azurerm_key_vault.chain.id
}
