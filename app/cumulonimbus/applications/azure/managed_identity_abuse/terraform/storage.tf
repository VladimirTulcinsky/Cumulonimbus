resource "azurerm_storage_account" "flag_storage" {
  name                     = "${var.app_name}mia${random_integer.managed_identity_abuse.result}"
  resource_group_name      = azurerm_resource_group.managed_identity_abuse.name
  location                 = azurerm_resource_group.managed_identity_abuse.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"

  # No public network access — only reachable via the managed identity token
  network_rules {
    default_action = "Deny"
    ip_rules       = [var.attacker_public_ip]
  }
}

resource "azurerm_storage_container" "flags" {
  name                  = "flags"
  storage_account_name  = azurerm_storage_account.flag_storage.name
  container_access_type = "private"
}

resource "azurerm_storage_blob" "flag" {
  name                   = "flag.txt"
  storage_account_name   = azurerm_storage_account.flag_storage.name
  storage_container_name = azurerm_storage_container.flags.name
  type                   = "Block"
  source_content         = "CUMULONIMBUS{M4n4g3d_1d3nt1ty_4bus3}\n"
}
