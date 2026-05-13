resource "random_id" "suffix" {
  byte_length = 4
}

locals {
  rg_name    = "cumulonimbus-${var.app_id}-${random_id.suffix.hex}"
  topic_name = "cnimbus-topic-${random_id.suffix.hex}"
}

resource "azurerm_resource_group" "rg" {
  name     = local.rg_name
  location = "West Europe"
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "azurerm_eventgrid_topic" "app" {
  name                = local.topic_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# Event subscription with the flag embedded as a token query parameter in the webhook URL
# The full webhook URL is returned in plaintext by ARM to any Reader
resource "azurerm_eventgrid_event_subscription" "notify" {
  name  = "production-notify"
  scope = azurerm_eventgrid_topic.app.id

  webhook_endpoint {
    url = "https://hooks.internal.example.com/events?token=CUMULONIMBUS{3v3ntGr1d_W3bh00k_T0k3n_3xp0s3d}&source=azure"
  }

  retry_policy {
    max_delivery_attempts = 3
    event_time_to_live    = 1440
  }
}

# Attacker user with Reader on the resource group — can list event subscriptions and see the webhook URL
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
