output "attacker_upn" {
  description = "Attacker Azure AD user principal name (starts with NO access)"
  value       = azuread_user.attacker.user_principal_name
}

output "attacker_password" {
  description = "Attacker Azure AD user password"
  value       = azuread_user.attacker.password
  sensitive   = true
}

output "resource_group_name" {
  description = "Resource group containing the chain"
  value       = azurerm_resource_group.rg.name
}

output "gatekeeper_url" {
  description = "Gatekeeper endpoint — submit flags here to unlock access"
  value       = "http://${azurerm_container_group.gatekeeper.fqdn}"
}

output "gatekeeper_ip" {
  description = "Gatekeeper public IP (fallback if DNS is slow)"
  value       = azurerm_container_group.gatekeeper.ip_address
}

output "start_here" {
  description = "Where to begin"
  value       = "Read the public blob: https://${azurerm_storage_account.sa.name}.blob.core.windows.net/public/welcome.txt"
}
