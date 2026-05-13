output "attacker_upn" {
  description = "Attacker Azure AD user principal name"
  value       = azuread_user.attacker.user_principal_name
}

output "attacker_password" {
  description = "Attacker Azure AD user password"
  value       = azuread_user.attacker.password
  sensitive   = true
}

output "vm_name" {
  description = "Virtual machine name"
  value       = azurerm_linux_virtual_machine.vm.name
}

output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.rg.name
}
