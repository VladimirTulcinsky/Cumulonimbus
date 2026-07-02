output "domain_name" {
  value = var.tenant_domain
}

output "user_name" {
  value = azuread_user.victim.user_principal_name
}

output "user_password" {
  value     = azuread_user.victim.password
  sensitive = true
}
