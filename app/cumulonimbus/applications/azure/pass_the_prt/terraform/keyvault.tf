resource "azurerm_key_vault" "ptp" {
  name                      = "kv-ptp-${random_id.suffix.hex}"
  location                  = azurerm_resource_group.ptp.location
  resource_group_name       = azurerm_resource_group.ptp.name
  tenant_id                 = data.azurerm_client_config.current.tenant_id
  sku_name                  = "standard"
  enable_rbac_authorization = true
  purge_protection_enabled  = false
}

resource "azurerm_role_assignment" "terraform_kv_secrets_officer" {
  scope                = azurerm_key_vault.ptp.id
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
  value        = "CUMULONIMBUS{PassThePRT_CloudLateralMovement_MFA_Bypass}"
  key_vault_id = azurerm_key_vault.ptp.id
}

# Only the victim user can read the flag, not the attacker's local account.
# Reader (control plane) makes the vault visible to the victim in the Azure
# portal; Key Vault Secrets User (data plane) lets them list the secrets and
# show the flag's value there.
resource "azurerm_role_assignment" "victim_kv_reader" {
  scope                = azurerm_key_vault.ptp.id
  role_definition_name = "Reader"
  principal_id         = azuread_user.victim.object_id
}

resource "azurerm_role_assignment" "victim_kv_secrets_user" {
  scope                = azurerm_key_vault.ptp.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azuread_user.victim.object_id
}
