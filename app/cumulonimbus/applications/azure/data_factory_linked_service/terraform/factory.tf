resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_resource_group" "lab" {
  name     = "${var.app_name}-${var.app_id}-${random_string.suffix.result}"
  location = "West Europe"

  tags = {
    app_id = var.app_id
  }
}

data "azuread_client_config" "current" {}

resource "azuread_application" "attacker" {
  display_name = "${var.app_name}-${var.app_id}-attacker-${random_string.suffix.result}"
}

resource "azuread_service_principal" "attacker" {
  client_id = azuread_application.attacker.client_id
}

resource "azuread_service_principal_password" "attacker" {
  service_principal_id = azuread_service_principal.attacker.id
}

resource "azurerm_role_assignment" "attacker_reader" {
  scope                = azurerm_resource_group.lab.id
  role_definition_name = "Reader"
  principal_id         = azuread_service_principal.attacker.id
}

resource "azurerm_data_factory" "lab" {
  name                = "${var.app_name}-adf-${random_string.suffix.result}"
  location            = azurerm_resource_group.lab.location
  resource_group_name = azurerm_resource_group.lab.name

  tags = {
    app_id = var.app_id
  }
}

resource "azurerm_data_factory_linked_service_azure_blob_storage" "lab" {
  name            = "DataLakeConnection"
  data_factory_id = azurerm_data_factory.lab.id
  description     = "Primary data lake storage connection"

  connection_string = "DefaultEndpointsProtocol=https;AccountName=cumulonimbusdata;AccountKey=CUMULONIMBUS{ADF_L1nk3d_S3rv1c3_Cl34rt3xt_K3y};EndpointSuffix=core.windows.net"
}

resource "azurerm_data_factory_linked_service_azure_blob_storage" "archive" {
  name            = "ArchiveStorageConnection"
  data_factory_id = azurerm_data_factory.lab.id
  description     = "Archive storage connection"

  connection_string = "DefaultEndpointsProtocol=https;AccountName=cumulonimbusarchive;AccountKey=YXJjaGl2ZWtleWZha2VmYWtlZmFrZWZha2VmYWtlZmFrZWZha2VmYWtlZmFrZQ==;EndpointSuffix=core.windows.net"
}
