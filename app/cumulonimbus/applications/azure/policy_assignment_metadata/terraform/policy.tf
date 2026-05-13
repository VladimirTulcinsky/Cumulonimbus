resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_resource_group" "lab" {
  name     = "${var.app_name}-${var.app_id}-${random_string.suffix.result}"
  location = "West Europe"

  tags = {
    app_id = var.app_id
  }
}

data "azuread_client_config" "current" {}

resource "azuread_application" "attacker" {
  display_name = "${var.app_name}-${var.app_id}-attacker-${random_string.suffix.result}"
}

resource "azuread_service_principal" "attacker" {
  client_id = azuread_application.attacker.client_id
}

resource "azuread_service_principal_password" "attacker" {
  service_principal_id = azuread_service_principal.attacker.id
}

resource "azurerm_role_assignment" "attacker_reader" {
  scope                = azurerm_resource_group.lab.id
  role_definition_name = "Reader"
  principal_id         = azuread_service_principal.attacker.id
}

data "azurerm_policy_definition" "audit_unmanaged_disks" {
  name = "06a78e20-9358-41c9-923c-fb736d382a4d"
}

resource "azurerm_resource_group_policy_assignment" "lab" {
  name                 = "cnimbus-${random_string.suffix.result}"
  resource_group_id    = azurerm_resource_group.lab.id
  policy_definition_id = data.azurerm_policy_definition.audit_unmanaged_disks.id
  display_name         = "Cumulonimbus Lab Policy"
  description          = "Audit VMs not using managed disks"

  metadata = jsonencode({
    internal-token  = "CUMULONIMBUS{P0l1cy_M3t4d4t4_S3cr3t_3xp0s3d}"
    environment     = "training"
    ticket-ref      = "SEC-1234"
    created-by      = "platform-team"
  })
}
