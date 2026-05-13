output "attacker_username" {
  value = azuread_user.attacker.user_principal_name
}

output "attacker_password" {
  value     = random_password.attacker.result
  sensitive = true
}

output "vm_name" {
  value = azurerm_linux_virtual_machine.managed_identity_abuse.name
}

output "resource_group_name" {
  value = azurerm_resource_group.managed_identity_abuse.name
}

output "storage_account_name" {
  value = azurerm_storage_account.flag_storage.name
}

output "cumulonimbus_id" {
  value = random_integer.managed_identity_abuse.result
}
