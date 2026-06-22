output "ctfd_url" {
  description = "Shared Azure CTFd scoreboard URL (give this to players)."
  value       = "http://${azurerm_public_ip.ctfd.ip_address}:8001"
}

output "public_ip" {
  value = azurerm_public_ip.ctfd.ip_address
}

output "ssh_command" {
  value = "ssh ${var.admin_username}@${azurerm_public_ip.ctfd.ip_address}"
}

output "admin_login" {
  description = "CTFd admin account."
  value       = "username: admin (password: the ctfd_admin_password you set)"
}

output "note" {
  value = "First boot installs Docker, clones the repo, and seeds CTFd — allow a few minutes after apply before the URL responds."
}
