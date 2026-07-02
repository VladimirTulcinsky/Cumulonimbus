output "domain_name" {
  value = var.tenant_domain
}

output "user_name" {
  value = azuread_user.attacker.user_principal_name
}

output "user_password" {
  value     = azuread_user.attacker.password
  sensitive = true
}
