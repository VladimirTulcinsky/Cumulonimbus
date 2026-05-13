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
  description = "Resource group containing the flag in its tags"
  value       = azurerm_resource_group.rg.name
}

output "subscription_id" {
  description = "Azure subscription ID"
  value       = data.azurerm_subscription.current.subscription_id
}
