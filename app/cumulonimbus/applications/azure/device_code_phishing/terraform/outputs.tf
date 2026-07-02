output "domain_name" {
  value = var.tenant_domain
}

output "user_name" {
  value = azuread_user.victim.user_principal_name
}

output "user_password" {
  value     = random_password.victim.result
  sensitive = true
}

output "storage_account_name" {
  value = azurerm_storage_account.flag.name
}

output "container_name" {
  value = azurerm_storage_container.data.name
}
