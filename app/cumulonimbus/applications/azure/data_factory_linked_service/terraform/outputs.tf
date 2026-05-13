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

output "data_factory_name" {
  value = azurerm_data_factory.lab.name
}

output "linked_service_name" {
  value = azurerm_data_factory_linked_service_azure_blob_storage.lab.name
}
