output "attacker_upn" {
  description = "Attacker Azure AD user principal name"
  value       = azuread_user.attacker.user_principal_name
}

output "attacker_password" {
  description = "Attacker Azure AD user password"
  value       = azuread_user.attacker.password
  sensitive   = true
}

output "config_store_name" {
  description = "App Configuration store name"
  value       = azurerm_app_configuration.config.name
}

output "config_store_endpoint" {
  description = "App Configuration store endpoint"
  value       = azurerm_app_configuration.config.endpoint
}

output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.rg.name
}
