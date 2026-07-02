resource "azuread_user" "policyuser" {
  user_principal_name   = "policyuser-${random_id.suffix.hex}@${var.tenant_domain}"
  display_name          = "Policy User ${random_id.suffix.hex}"
  password              = "P0licyUs3r!${random_id.suffix.hex}"
  force_password_change = false
}

# Resource Policy Contributor allows writing policy definitions, initiatives,
# and assignments — but is not typically considered a privileged role.
resource "azurerm_role_assignment" "policyuser_rpc" {
  scope                = "/subscriptions/${var.subscription_id}"
  role_definition_name = "Resource Policy Contributor"
  principal_id         = azuread_user.policyuser.object_id
}
