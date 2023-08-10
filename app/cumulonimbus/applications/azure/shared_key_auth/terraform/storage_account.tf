resource "azurerm_resource_group" "ska_sa" {
  name     = "ska-sa-rg"
  location = "West Europe"
}


resource "azurerm_storage_account" "ska_sa" {
  name                     = "stska${var.app_name}${random_integer.ska.result}"
  resource_group_name      = azurerm_resource_group.ska_sa.name
  location                 = azurerm_resource_group.ska_sa.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  /* network_rules {
    default_action = "Deny"
    ip_rules       = [var.attacker_public_ip]
  } */
}




