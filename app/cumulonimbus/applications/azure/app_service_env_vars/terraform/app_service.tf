resource "random_id" "suffix" {
  byte_length = 4
}

locals {
  rg_name      = "cumulonimbus-${var.app_id}-${random_id.suffix.hex}"
  service_name = "cnimbus-app-${random_id.suffix.hex}"
}

resource "azurerm_resource_group" "rg" {
  name     = local.rg_name
  location = "West Europe"
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }

  depends_on = [azurerm_resource_provider_registration.microsoft_web]
}

resource "azurerm_service_plan" "plan" {
  name                = "cnimbus-plan-${random_id.suffix.hex}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "B1"
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "azurerm_linux_web_app" "app" {
  name                = local.service_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.plan.id

  site_config {
    application_stack {
      python_version = "3.11"
    }
  }

  # Secrets stored as plain app settings — readable via the Azure portal and ARM API
  app_settings = {
    "DATABASE_URL"       = "postgresql://admin:Sup3rS3cr3tDBPass@prod-db.internal:5432/appdb"
    "SECRET_FLAG"        = "CUMULONIMBUS{App_S3rv1c3_Env_V4rs_3xp0s3d}"
    "STORAGE_ACCESS_KEY" = "STORAGE_KEY_cmlnmbs_abcdefghijklmnopqrstuvwx"
    "ENVIRONMENT"        = "production"
  }

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# Attacker user assigned Website Contributor at resource group scope
# This grants Microsoft.Web/sites/config/list which returns app settings
data "azuread_client_config" "current" {}

resource "azuread_user" "attacker" {
  user_principal_name = "attacker-${random_id.suffix.hex}@${var.tenant_domain}"
  display_name        = "Cumulonimbus Attacker ${random_id.suffix.hex}"
  password            = "C@ttack3r!${random_id.suffix.hex}"
  force_password_change = false
}

data "azurerm_subscription" "current" {}

resource "azurerm_role_assignment" "attacker_website_contributor" {
  scope                = azurerm_resource_group.rg.id
  role_definition_name = "Website Contributor"
  principal_id         = azuread_user.attacker.object_id
}
