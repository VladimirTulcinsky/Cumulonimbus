output "resource_group_name" {
  description = "Resource group holding the whole chain"
  value       = azurerm_resource_group.rg.name
}

output "portal_website_account" {
  description = "Storage account serving the public portal (start here)"
  value       = azurerm_storage_account.pub.name
}

output "portal_website_url" {
  description = "Public static-website endpoint of the portal (app.js leaks a SAS token)"
  value       = azurerm_storage_account.pub.primary_web_endpoint
}

output "starting_point" {
  description = "Where the player begins"
  value       = "Browse the portal website and read its app.js — it hardcodes a SAS token."
}
