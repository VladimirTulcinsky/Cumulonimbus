output "web_endpoint" {
  value = azurerm_storage_account.blob_sas_abuse.primary_web_endpoint
}

output "app_js_url" {
  value = "${azurerm_storage_account.blob_sas_abuse.primary_web_endpoint}app.js"
}

output "storage_account_name" {
  value = azurerm_storage_account.blob_sas_abuse.name
}

output "cumulonimbus_id" {
  value = random_integer.blob_sas_abuse.result
}
