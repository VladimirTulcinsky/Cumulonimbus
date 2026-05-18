resource "azurerm_resource_group" "target" {
  name     = "policy-privesc-target-${random_id.suffix.hex}"
  location = "westeurope"
}

# No "monitoring" tag — non-compliant with the initiative, which gives a
# concrete resource to run a remediation task against.
resource "azurerm_storage_account" "target" {
  depends_on                      = [time_sleep.rbac_propagation]
  name                            = "pp${random_id.suffix.hex}"
  resource_group_name             = azurerm_resource_group.target.name
  location                        = azurerm_resource_group.target.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  allow_nested_items_to_be_public = false
}

resource "azurerm_storage_container" "secrets" {
  name                  = "secrets"
  storage_account_name  = azurerm_storage_account.target.name
  container_access_type = "private"
}

resource "azurerm_storage_blob" "flag" {
  name                   = "flag.txt"
  storage_account_name   = azurerm_storage_account.target.name
  storage_container_name = azurerm_storage_container.secrets.name
  type                   = "Block"
  source_content         = "CUMULONIMBUS{PolicyPrivEsc_DeployIfNotExists_OwnerRole}"
}
