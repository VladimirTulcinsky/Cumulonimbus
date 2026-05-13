output "attacker_username" {
  value = azuread_user.attacker.user_principal_name
}

output "attacker_password" {
  value     = random_password.attacker.result
  sensitive = true
}

output "automation_account_name" {
  value = azurerm_automation_account.automation_account.name
}

output "resource_group_name" {
  value = azurerm_resource_group.automation_account.name
}

output "storage_account_name" {
  value = azurerm_storage_account.flag.name
}

output "cumulonimbus_id" {
  value = random_integer.automation_account.result
}
