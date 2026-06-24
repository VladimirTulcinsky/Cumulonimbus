###############################################################################
# S8 — Key Vault holding the flag. The portal service principal already has
# "Key Vault Secrets User", so once the player discovers the vault and secret
# name (from the Container Instance env vars in S7) they can read the flag.
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

# RBAC takes a moment to propagate before the data-plane write will succeed.
resource "time_sleep" "kv_rbac_propagation" {
  depends_on      = [azurerm_role_assignment.deployer_kv_officer]
  create_duration = "30s"
}

resource "azurerm_key_vault_secret" "flag" {
  depends_on   = [time_sleep.kv_rbac_propagation]
  name         = local.kv_secret
  value        = "CUMULONIMBUS{Pl41nt3xt_Cr3d_Ch41n_2_K3yV4ult}"
  key_vault_id = azurerm_key_vault.chain.id
}

# The attacker's service principal can read secrets (the final payoff).
resource "azurerm_role_assignment" "portal_kv_user" {
  scope                = azurerm_key_vault.chain.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azuread_service_principal.portal.object_id
}
