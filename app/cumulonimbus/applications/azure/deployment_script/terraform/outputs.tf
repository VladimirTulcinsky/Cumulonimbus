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

output "deployment_script_name" {
  value = azurerm_resource_deployment_script_azure_cli.lab.name
}
