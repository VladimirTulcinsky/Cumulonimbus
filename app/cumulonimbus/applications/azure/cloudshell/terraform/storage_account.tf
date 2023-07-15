resource "azurerm_resource_group" "iam_cs" {
  name     = "iam-cs-rg"
  location = "West Europe"
}

resource "random_integer" "iam_cs" {
  min = 1
  max = 999999
}

resource "azurerm_storage_account" "iam_cs" {
  name                     = "stcs${var.app_name}${random_integer.iam_cs.result}"
  resource_group_name      = azurerm_resource_group.iam_cs.name
  location                 = azurerm_resource_group.iam_cs.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_share" "iam_cs" {
  name                 = "iamcs"
  storage_account_name = azurerm_storage_account.iam_cs.name
  quota                = 50
}

resource "azurerm_storage_share_directory" "iam_cs" {
  name                 = ".cloudconsole"
  share_name           = azurerm_storage_share.iam_cs.name
  storage_account_name = azurerm_storage_account.iam_cs.name
}

resource "azurerm_storage_share_file" "iam_cs" {
  name             = "acc_noher.img"
  storage_share_id = azurerm_storage_share.iam_cs.id
  source           = "../files/acc_noher.img"
  path             = azurerm_storage_share_directory.iam_cs.name
}
