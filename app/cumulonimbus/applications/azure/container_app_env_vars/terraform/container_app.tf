resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_resource_group" "lab" {
  name     = "${var.app_name  depends_on = [azurerm_resource_provider_registration.microsoft_app, azurerm_resource_provider_registration.microsoft_operationalinsights]
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

resource "azurerm_log_analytics_workspace" "lab" {
  name                = "${var.app_name}-${var.app_id}-law-${random_string.suffix.result}"
  location            = azurerm_resource_group.lab.location
  resource_group_name = azurerm_resource_group.lab.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = { app_id = var.app_id }
}

resource "azurerm_container_app_environment" "lab" {
  name                       = "${var.app_name}-${var.app_id}-env-${random_string.suffix.result}"
  location                   = azurerm_resource_group.lab.location
  resource_group_name        = azurerm_resource_group.lab.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.lab.id

  tags = { app_id = var.app_id }
}

resource "azurerm_container_app" "lab" {
  name                         = "${var.app_name}-${var.app_id}-${random_string.suffix.result}"
  container_app_environment_id = azurerm_container_app_environment.lab.id
  resource_group_name          = azurerm_resource_group.lab.name
  revision_mode                = "Single"

  template {
    container {
      name   = "app"
      image  = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name  = "APP_ENV"
        value = "production"
      }

      env {
        name  = "APP_VERSION"
        value = "1.0.0"
      }

      env {
        name  = "SECRET_FLAG"
        value = "CUMULONIMBUS{C0nt41n3r_App_Env_V4rs_3xp0s3d}"
      }

      env {
        name  = "DB_CONNECTION_STRING"
        value = "Server=db.cumulonimbus.local;Database=appdb;User=appuser;"
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 80

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  tags = { app_id = var.app_id }
}
