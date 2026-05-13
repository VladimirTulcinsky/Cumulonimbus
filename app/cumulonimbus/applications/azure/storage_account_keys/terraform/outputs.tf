output "attacker_upn" {
  description = "Attacker Azure AD user principal name"
  value       = azuread_user.attacker.user_principal_name
}

output "attacker_password" {
  description = "Attacker Azure AD user password"
  value       = azuread_user.attacker.password
  sensitive   = true
}

output "storage_account_name" {
  description = "Storage account name"
  value       = azurerm_storage_account.sa.name
}

output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.rg.name
}

output "container_name" {
  description = "Private container holding the flag blob"
  value       = azurerm_storage_container.secrets.name
}
