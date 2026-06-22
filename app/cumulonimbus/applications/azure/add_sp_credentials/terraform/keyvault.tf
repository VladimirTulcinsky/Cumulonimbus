# The payoff for the privilege escalation. Membership of the cred-administrators
# group grants the "Key Vault Secrets User" RBAC role on this vault, so once the
# attacker adds themselves to the group they can read the flag secret. This makes
# the group membership a *real* privilege via Azure RBAC, without needing a
# directory role (e.g. Global Administrator) that would require an Entra ID P1
# license — which is exactly why such RBAC-on-a-group misconfigurations are
# common in the real world.
resource "azurerm_key_vault" "flag" {
  name                      = "cumaddsp${random_integer.suffix.result}"
  location                  = azurerm_resource_group.rg.location
  resource_group_name       = azurerm_resource_group.rg.name
  tenant_id                 = var.tenant_id
  sku_name                  = "standard"
  enable_rbac_authorization = true
  purge_protection_enabled  = false
}

# Let the deploying service principal write the secret. (It typically already has
# Key Vault Administrator at subscription scope per the prerequisites; this makes
# the lab self-contained.)
resource "azurerm_role_assignment" "tf_kv_admin" {
  scope                = azurerm_key_vault.flag.id
  role_definition_name = "Key Vault Administrator"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_key_vault_secret" "flag" {
  name         = "flag"
  value        = "CUMULONIMBUS{SP_0wn3rsh1p_T0_K3yV4ult_Acc3ss}"
  key_vault_id = azurerm_key_vault.flag.id

  depends_on = [azurerm_role_assignment.tf_kv_admin]
}

# The real privilege the escalation unlocks: members of cred-administrators can
# read secrets from the vault.
resource "azurerm_role_assignment" "group_kv_reader" {
  scope                = azurerm_key_vault.flag.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azuread_group.administrators.object_id
}
