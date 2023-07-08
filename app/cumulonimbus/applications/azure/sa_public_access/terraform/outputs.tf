output "primary_web_endpoint" {
  value = azurerm_storage_account.sa_public_access.primary_web_host
}

output "cumulonimbus_id" {
  value = random_integer.sa_public_access.result
}
