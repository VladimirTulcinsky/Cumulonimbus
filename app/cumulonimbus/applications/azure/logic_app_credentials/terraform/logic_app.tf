resource "random_id" "suffix" {
  byte_length = 4
}

locals {
  rg_name       = "cumulonimbus-${var.app_id}-${random_id.suffix.hex}"
  workflow_name = "cnimbus-workflow-${random_id.suffix.hex}"
}

resource "azurerm_resource_group" "rg" {
  name     = local.rg_name
  location = "West Europe"
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }

  depends_on = [azurerm_resource_provider_registration.microsoft_logic]
}

# Logic App workflow with an HTTP action containing hardcoded credentials in headers
resource "azurerm_logic_app_workflow" "app" {
  name                = local.workflow_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "azurerm_logic_app_trigger_recurrence" "hourly" {
  name         = "Recurrence"
  logic_app_id = azurerm_logic_app_workflow.app.id
  frequency    = "Hour"
  interval     = 1
}

resource "azurerm_logic_app_action_http" "notify" {
  name         = "Notify-Backend"
  logic_app_id = azurerm_logic_app_workflow.app.id
  method       = "POST"
  uri          = "https://api.internal.example.com/notify"

  headers = {
    "Content-Type"  = "application/json"
    "Authorization" = "Bearer CUMULONIMBUS{L0g1c_App_H4rdcod3d_Cr3d3nt14ls}"
    "X-Service-Key" = "svc_cmlnmbs_internal_notify_key"
  }

  body = jsonencode({
    event = "hourly_sync"
  })
}

# Attacker user with Reader on the resource group — can dump the workflow definition
data "azuread_client_config" "current" {}

resource "azuread_user" "attacker" {
  user_principal_name   = "attacker-${random_id.suffix.hex}@${data.azuread_client_config.current.tenant_id}.onmicrosoft.com"
  display_name          = "Cumulonimbus Attacker ${random_id.suffix.hex}"
  password              = "C@ttack3r!${random_id.suffix.hex}"
  force_password_change = false
}

resource "azurerm_role_assignment" "attacker_reader" {
  scope                = azurerm_resource_group.rg.id
  role_definition_name = "Reader"
  principal_id         = azuread_user.attacker.object_id
}
