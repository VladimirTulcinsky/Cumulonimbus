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

output "container_app_name" {
  value = azurerm_container_app.lab.name
}

output "container_app_fqdn" {
  value = azurerm_container_app.lab.ingress[0].fqdn
}
