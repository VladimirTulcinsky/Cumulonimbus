output "domain_name" {
  value = data.azuread_domains.aad_domains.domains.*.domain_name[0]
}

output "user_name" {
  value = azuread_user.norightsuser.user_principal_name
}

output "user_password" {
  value     = azuread_user.norightsuser.password
  sensitive = true
}

output "app_registration" {
  value = azuread_application.group-add-app.display_name
}

output "admin_group" {
  value = azuread_group.administrators.display_name
}

