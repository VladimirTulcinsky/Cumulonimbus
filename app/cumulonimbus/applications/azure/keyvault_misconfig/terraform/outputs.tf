output "attacker_username" {
  value = azuread_user.attacker.user_principal_name
}

output "attacker_password" {
  value     = random_password.attacker.result
  sensitive = true
}

output "key_vault_name" {
  value = azurerm_key_vault.keyvault_misconfig.name
}

output "key_vault_uri" {
  value = azurerm_key_vault.keyvault_misconfig.vault_uri
}

output "resource_group_name" {
  value = azurerm_resource_group.keyvault_misconfig.name
}

output "cumulonimbus_id" {
  value = random_integer.keyvault_misconfig.result
}
