resource "random_id" "suffix" {
  byte_length = 4
}

# Resource group with sensitive credentials stored as tags — a common operational mistake
# Engineers sometimes tag RGs with service principal secrets "for convenience"
resource "azurerm_resource_group" "rg" {
  name     = "cumulonimbus-${var.app_id}-${random_id.suffix.hex}"
  location = "West Europe"

  tags = {
    app_id                   = var.app_id
    managed                  = "terraform"
    environment              = "production"
    owner                    = "platform-team@example.com"
    "service-principal-id"   = "sp-deploy-prod-${random_id.suffix.hex}"
    "service-principal-secret" = "CUMULONIMBUS{S3cr3t_1n_R3s0urc3_Gr0up_T4gs}"
    "deployment-key"         = "deploy_cmlnmbs_${random_id.suffix.hex}"
  }
}

# Attacker user with Reader on the subscription — can enumerate all resource groups and their tags
data "azuread_client_config" "current" {}
data "azurerm_subscription" "current" {}

resource "azuread_user" "attacker" {
  user_principal_name   = "attacker-${random_id.suffix.hex}@${var.tenant_domain}"
  display_name          = "Cumulonimbus Attacker ${random_id.suffix.hex}"
  password              = "C@ttack3r!${random_id.suffix.hex}"
  force_password_change = false
}

resource "azurerm_role_assignment" "attacker_reader" {
  scope                = data.azurerm_subscription.current.id
  role_definition_name = "Reader"
  principal_id         = azuread_user.attacker.object_id
}
