output "vm_public_ip" {
  value = azurerm_public_ip.ptp.ip_address
}

output "attacker_username" {
  value = "attacker"
}

output "attacker_password" {
  value     = random_password.attacker.result
  sensitive = true
}

output "victim_upn" {
  value = azuread_user.victim.user_principal_name
}

output "victim_password" {
  value     = random_password.victim.result
  sensitive = true
}

output "keyvault_name" {
  value = azurerm_key_vault.ptp.name
}

output "keyvault_uri" {
  value = azurerm_key_vault.ptp.vault_uri
}

output "resource_group" {
  value = azurerm_resource_group.ptp.name
}
