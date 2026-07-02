output "domain_name" {
  value = var.tenant_domain
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

