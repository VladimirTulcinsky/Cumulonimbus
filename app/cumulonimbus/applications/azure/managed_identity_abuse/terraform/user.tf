
resource "random_password" "attacker" {
  length           = 16
  special          = true
  override_special = "!@#"
  min_upper        = 2
  min_numeric      = 2
}

resource "azuread_user" "attacker" {
  user_principal_name = "mia-attacker@${var.tenant_domain}"
  display_name        = "MIA Attacker"
  mail_nickname       = "mia-attacker"
  password            = random_password.attacker.result
  force_password_change = false
}

# Attacker has Virtual Machine Contributor — can invoke run-commands but not read storage directly
resource "azurerm_role_assignment" "attacker_vm_contributor" {
  scope                = azurerm_linux_virtual_machine.managed_identity_abuse.id
  role_definition_name = "Virtual Machine Contributor"
  principal_id         = azuread_user.attacker.object_id
}
