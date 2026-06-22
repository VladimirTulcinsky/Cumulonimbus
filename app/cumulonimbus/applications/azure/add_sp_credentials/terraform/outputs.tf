output "domain_name" {
  value = var.tenant_domain
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

output "key_vault_name" {
  value = azurerm_key_vault.flag.name
}

