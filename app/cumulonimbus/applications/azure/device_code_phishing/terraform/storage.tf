resource "azurerm_storage_account" "flag" {
  name                     = "cumdcp${random_integer.suffix.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  blob_properties {
    versioning_enabled = false
  }
}

resource "azurerm_storage_container" "data" {
  name                  = "sensitive-data"
  storage_account_name  = azurerm_storage_account.flag.name
  container_access_type = "private"
}

resource "azurerm_storage_blob" "flag" {
  name                   = "flag.txt"
  storage_account_name   = azurerm_storage_account.flag.name
  storage_container_name = azurerm_storage_container.data.name
  type                   = "Block"
  source_content         = "CUMULONIMBUS{D3v1c3_C0d3_Ph1sh1ng_W0rks}"
}
