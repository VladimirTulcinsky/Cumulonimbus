output "attacker_username" {
  value = azuread_user.attacker.user_principal_name
}

output "attacker_password" {
  value     = random_password.attacker.result
  sensitive = true
}

output "resource_group_name" {
  value = azurerm_resource_group.arm_deployment_history.name
}

output "deployment_name" {
  value = azurerm_resource_group_template_deployment.app_infra.name
}

output "cumulonimbus_id" {
  value = random_integer.arm_deployment_history.result
}
