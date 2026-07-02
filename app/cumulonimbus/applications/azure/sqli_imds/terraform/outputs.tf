output "vm_public_ip" {
  value = azurerm_public_ip.sqli_imds.ip_address
}

output "keyvault_name" {
  value = azurerm_key_vault.sqli_imds.name
}

output "keyvault_uri" {
  value = azurerm_key_vault.sqli_imds.vault_uri
}

output "resource_group" {
  value = azurerm_resource_group.sqli_imds.name
}
