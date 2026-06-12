resource "azurerm_resource_group" "ska_sa" {
  name     = "ska-sa-rg${local.name_suffix_dash}"
  location = var.location
}

resource "time_sleep" "ska_sa_rg_propagation" {
  depends_on      = [azurerm_resource_group.ska_sa]
  create_duration = "15s"
}

resource "azurerm_storage_account" "ska_sa" {
  depends_on               = [time_sleep.ska_sa_rg_propagation]
  name                     = "stska${var.app_name}${random_integer.ska.result}"
  resource_group_name      = azurerm_resource_group.ska_sa.name
  location                 = azurerm_resource_group.ska_sa.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}




