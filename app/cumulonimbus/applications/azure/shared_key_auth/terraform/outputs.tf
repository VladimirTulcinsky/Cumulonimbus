output "domain_name" {
  value = data.azuread_domains.aad_domains.domains.*.domain_name[0]
}

output "user_name" {
  value = azuread_user.attacker.user_principal_name
}

output "user_password" {
  value     = azuread_user.attacker.password
  sensitive = true
}
