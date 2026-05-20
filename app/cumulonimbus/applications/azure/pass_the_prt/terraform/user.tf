resource "azuread_user" "victim" {
  user_principal_name   = "ptp-victim-${random_id.suffix.hex}@${var.tenant_domain}"
  display_name          = "PTP Victim ${random_id.suffix.hex}"
  password              = random_password.victim.result
  force_password_change = false
}

# Allows the victim to RDP into the Azure AD-joined VM using their Entra credentials.
# When they sign in, CloudAP issues a PRT that is stored in LSASS.
resource "azurerm_role_assignment" "victim_vm_login" {
  scope                = azurerm_windows_virtual_machine.ptp.id
  role_definition_name = "Virtual Machine User Login"
  principal_id         = azuread_user.victim.object_id
}

# Safety net: force-delete the Entra ID user on destroy after all role assignments
# are removed. The azuread provider may silently skip deletion; this ensures cleanup.
resource "null_resource" "victim_user_cleanup" {
  triggers = {
    upn = azuread_user.victim.user_principal_name
  }

  provisioner "local-exec" {
    when    = destroy
    command = "az ad user delete --id '${self.triggers.upn}' 2>/dev/null || true"
  }

  depends_on = [
    azurerm_role_assignment.victim_vm_login,
    azurerm_role_assignment.victim_kv_secrets_user,
  ]
}
