output "attacker_upn" {
  description = "Attacker Azure AD user principal name"
  value       = azuread_user.attacker.user_principal_name
}

output "attacker_password" {
  description = "Attacker Azure AD user password"
  value       = azuread_user.attacker.password
  sensitive   = true
}

output "resource_group_name" {
  description = "Resource group the attacker has Reader on"
  value       = azurerm_resource_group.rg.name
}

output "acr_login_server" {
  description = "Login server of the private container registry"
  value       = azurerm_container_registry.acr.login_server
}

output "leak_storage_account" {
  description = "Storage account whose tags leak the registry admin credentials"
  value       = azurerm_storage_account.leak.name
}

output "image_reference" {
  description = "Repository:tag of the lab image in the registry"
  value       = local.image_ref
}
