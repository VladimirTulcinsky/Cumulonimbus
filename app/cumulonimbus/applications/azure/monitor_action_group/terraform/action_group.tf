resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_resource_group" "lab" {
  name     = "${var.app_name  depends_on = [azurerm_resource_provider_registration.microsoft_insights]
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

resource "azurerm_monitor_action_group" "lab" {
  name                = "${var.app_name}-${var.app_id}-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.lab.name
  short_name          = "cnimbus"

  webhook_receiver {
    name        = "security-alerts"
    service_uri = "https://webhook.cumulonimbus.local/alerts?token=CUMULONIMBUS{Monit0r_W3bh00k_T0k3n_3xp0s3d}"
  }

  email_receiver {
    name          = "ops-team"
    email_address = "ops@cumulonimbus.local"
  }

  tags = {
    app_id = var.app_id
  }
}

resource "azurerm_monitor_metric_alert" "lab" {
  name                = "${var.app_name}-${var.app_id}-alert-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.lab.name
  scopes              = [azurerm_resource_group.lab.id]
  description         = "High CPU alert for training lab"
  severity            = 2

  criteria {
    metric_namespace = "Microsoft.Compute/virtualMachines"
    metric_name      = "Percentage CPU"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 90
  }

  action {
    action_group_id = azurerm_monitor_action_group.lab.id
  }

  tags = {
    app_id = var.app_id
  }
}
