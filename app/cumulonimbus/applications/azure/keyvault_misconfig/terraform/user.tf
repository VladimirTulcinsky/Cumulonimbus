
resource "random_password" "attacker" {
  length           = 16
  special          = true
  override_special = "!@#"
  min_upper        = 2
  min_numeric      = 2
}

resource "azuread_user" "attacker" {
  user_principal_name   = "kv-attacker@${var.tenant_domain}"
  display_name          = "KV Attacker"
  mail_nickname         = "kv-attacker"
  password              = random_password.attacker.result
  force_password_change = false
}

# Reader on the resource group so the attacker can discover the Key Vault
resource "azurerm_role_assignment" "attacker_reader" {
  scope                = azurerm_resource_group.keyvault_misconfig.id
  role_definition_name = "Reader"
  principal_id         = azuread_user.attacker.object_id
}
