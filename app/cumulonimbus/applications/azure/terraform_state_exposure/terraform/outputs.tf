output "storage_account_name" {
  value = azurerm_storage_account.tfstate.name
}

output "state_blob_url" {
  value = "${azurerm_storage_account.tfstate.primary_blob_endpoint}tfstate/production/terraform.tfstate"
}

output "resource_group_name" {
  value = azurerm_resource_group.terraform_state_exposure.name
}

output "cumulonimbus_id" {
  value = random_integer.terraform_state_exposure.result
}
