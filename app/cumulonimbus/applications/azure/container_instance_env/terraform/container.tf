resource "random_id" "suffix" {
  byte_length = 4
}

locals {
  rg_name        = "cumulonimbus-${var.app_id}-${random_id.suffix.hex}"
  container_name = "cnimbus-app-${random_id.suffix.hex}"
}

resource "azurerm_resource_group" "rg" {
  name     = local.rg_name
  location = "West Europe"
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }

  depends_on = [azurerm_resource_provider_registration.microsoft_containerinstance]
}

resource "azurerm_container_group" "app" {
  name                = local.container_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  ip_address_type     = "None"
  os_type             = "Linux"
  restart_policy      = "Never"

  container {
    name   = "app"
    image  = "alpine:3.18"
    cpu    = "0.5"
    memory = "0.5"

    commands = ["sh", "-c", "echo Starting application && sleep 3600"]

    # Plain environment variables — visible to anyone who can describe the container
    environment_variables = {
      "APP_VERSION"   = "2.4.1"
      "ENVIRONMENT"   = "production"
      "DATABASE_HOST" = "prod-db.internal.example.com"
      "SECRET_FLAG"   = "CUMULONIMBUS{C0nt41n3r_1nst4nc3_Pl41nt3xt_Env}"
    }

    secure_environment_variables = {}

    ports {
      port     = 8080
      protocol = "TCP"
    }
  }

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# Attacker user with Reader on resource group — az container show returns all env vars
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
