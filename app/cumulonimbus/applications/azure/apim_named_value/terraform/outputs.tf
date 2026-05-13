output "attacker_client_id" {
  value = azuread_application.attacker.client_id
}

output "attacker_client_secret" {
  value     = azuread_service_principal_password.attacker.value
  sensitive = true
}

output "resource_group_name" {
  value = azurerm_resource_group.lab.name
}

output "apim_name" {
  value = azurerm_api_management.lab.name
}

output "named_value_id" {
  value = azurerm_api_management_named_value.flag.name
}
