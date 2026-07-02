output "function_url" {
  value = "https://${azurerm_linux_function_app.function_ssrf.default_hostname}/api/fetch"
}

output "storage_account_name" {
  value = azurerm_storage_account.flag.name
}

output "resource_group_name" {
  value = azurerm_resource_group.function_ssrf.name
}

output "cumulonimbus_id" {
  value = random_integer.function_ssrf.result
}
