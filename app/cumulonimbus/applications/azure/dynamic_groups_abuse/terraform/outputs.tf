output "domain_name" {
  value = var.tenant_domain
}

output "user_name" {
  value = azuread_user.attacker.user_principal_name
}

output "user_password" {
  value     = random_password.attacker.result
  sensitive = true
}

output "key_vault_name" {
  value = azurerm_key_vault.flag.name
}

output "group_name" {
  value = azuread_group.security_team.display_name
}
