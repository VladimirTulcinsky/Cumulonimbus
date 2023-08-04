output "domain_name" {
  value = data.azuread_domains.aad_domains.domains.*.domain_name[0]
}

output "admin_name" {
  value = azuread_user.administrator.user_principal_name
}

output "admin_password" {
  value     = azuread_user.administrator.password
  sensitive = true
}

output "norightsuser_name" {
  value = azuread_user.norightsuser.user_principal_name
}

output "norightsuser_password" {
  value     = azuread_user.norightsuser.password
  sensitive = true
}

