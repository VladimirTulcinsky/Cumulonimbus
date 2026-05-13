output "config_blob_url" {
  value = "${azurerm_storage_account.config.primary_blob_endpoint}config/config.json"
}

output "storage_account_name" {
  value = azurerm_storage_account.config.name
}

output "flag_storage_account" {
  value = azurerm_storage_account.flag.name
}

output "resource_group_name" {
  value = azurerm_resource_group.exposed_app_registration.name
}

output "cumulonimbus_id" {
  value = random_integer.exposed_app_registration.result
}
