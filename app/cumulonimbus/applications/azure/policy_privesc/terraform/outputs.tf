output "policyuser_upn" {
  value = azuread_user.policyuser.user_principal_name
}

output "policyuser_password" {
  value     = azuread_user.policyuser.password
  sensitive = true
}

output "subscription_id" {
  value = var.subscription_id
}

output "target_resource_group" {
  value = azurerm_resource_group.target.name
}

output "target_storage_account" {
  value = azurerm_storage_account.target.name
}

output "initiative_name" {
  value = azurerm_policy_set_definition.monitoring_initiative.name
}

output "policy_assignment_id" {
  value = azurerm_subscription_policy_assignment.monitoring_assignment.id
}

output "managed_identity_principal_id" {
  value = azurerm_subscription_policy_assignment.monitoring_assignment.identity[0].principal_id
}
