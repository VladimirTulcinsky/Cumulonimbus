data "azurerm_client_config" "current" {}

resource "random_integer" "keyvault_misconfig" {
  min = 1
  max = 999999
}

resource "azurerm_resource_group" "keyvault_misconfig" {
  name     = "keyvault-misconfig"
  location = "West Europe"
}

# Misconfigured Key Vault: access policy mode, public network access, no firewall
resource "azurerm_key_vault" "keyvault_misconfig" {
  name                = "kv-cmlnmbs-${random_integer.keyvault_misconfig.result}"
  location            = azurerm_resource_group.keyvault_misconfig.location
  resource_group_name = azurerm_resource_group.keyvault_misconfig.name
  tenant_id           = var.tenant_id
  sku_name            = "standard"

  # Misconfiguration 1: public network access with no firewall rules
  public_network_access_enabled = true

  # Misconfiguration 2: access policies mode (easier to accidentally over-grant than RBAC)
  enable_rbac_authorization = false

  soft_delete_retention_days = 7
}

# Deployer access policy — needed to write the flag secret
resource "azurerm_key_vault_access_policy" "deployer" {
  key_vault_id = azurerm_key_vault.keyvault_misconfig.id
  tenant_id    = var.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  secret_permissions = ["Get", "List", "Set", "Delete", "Purge"]
}

# Misconfiguration 3: overly permissive access policy granted to the attacker user
# (intended to only grant access to a specific application, but was applied to a user)
resource "azurerm_key_vault_access_policy" "attacker" {
  key_vault_id = azurerm_key_vault.keyvault_misconfig.id
  tenant_id    = var.tenant_id
  object_id    = azuread_user.attacker.object_id

  secret_permissions = ["Get", "List"]
}

resource "azurerm_key_vault_secret" "flag" {
  name         = "flag"
  value        = "CUMULONIMBUS{K3yV4ult_4cc3ss_P0l1cy_T00_Br04d}"
  key_vault_id = azurerm_key_vault.keyvault_misconfig.id

  depends_on = [azurerm_key_vault_access_policy.deployer]
}
