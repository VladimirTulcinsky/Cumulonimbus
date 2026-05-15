resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_resource_group" "lab" {
  name     = "${var.app_name  depends_on = [azurerm_resource_provider_registration.microsoft_managedidentity]
}-${var.app_id}-${random_string.suffix.result}"
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

resource "azurerm_user_assigned_identity" "script_runner" {
  name                = "${var.app_name}-${var.app_id}-id-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.lab.name
  location            = azurerm_resource_group.lab.location
}

resource "azurerm_role_assignment" "script_runner_contributor" {
  scope                = azurerm_resource_group.lab.id
  role_definition_name = "Contributor"
  principal_id         = azurerm_user_assigned_identity.script_runner.principal_id
}

resource "azurerm_resource_deployment_script_azure_cli" "lab" {
  name                = "${var.app_name}-${var.app_id}-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.lab.name
  location            = azurerm_resource_group.lab.location
  version             = "2.40.0"
  retention_interval  = "P1D"
  cleanup_preference  = "OnExpiration"

  script_content = <<-SCRIPT
    echo '{"flag":"CUMULONIMBUS{D3pl0ym3nt_Scr1pt_0utput_3xp0s3d}","environment":"training","status":"completed"}' > $AZ_SCRIPTS_OUTPUT_PATH
  SCRIPT

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.script_runner.id]
  }

  depends_on = [azurerm_role_assignment.script_runner_contributor]

  tags = {
    app_id = var.app_id
  }
}
