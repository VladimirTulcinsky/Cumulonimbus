resource "random_id" "suffix" {
  byte_length = 4
}

locals {
  # Registry and storage-account names must be globally unique and lowercase
  # alphanumeric (no dashes). Fold the optional per-player suffix down to safe
  # characters and keep within Azure's length limits.
  suffix_alnum = lower(replace(var.name_suffix, "/[^a-zA-Z0-9]/", ""))
  base         = "${local.suffix_alnum}${random_id.suffix.hex}"

  rg_name   = "cumulonimbus-${var.app_id}-${random_id.suffix.hex}"
  acr_name  = substr("cnacr${local.base}", 0, 50)
  sa_name   = substr("cnacrleak${local.base}", 0, 24)
  image_ref = "cumulonimbus/app:latest"
}

resource "azurerm_resource_group" "rg" {
  name     = local.rg_name
  location = var.location

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }

  depends_on = [azurerm_resource_provider_registration.microsoft_containerregistry]
}

# Private container registry. The admin account is enabled (a common
# convenience setting) — its username/password are powerful static credentials
# that grant full push/pull. A plain Reader CANNOT list these via the control
# plane; the lab leaks them elsewhere (see the storage account below).
resource "azurerm_container_registry" "acr" {
  name                = local.acr_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# Build the lab image server-side with ACR Tasks (`az acr build`) so no local
# Docker daemon is required. The image hides a secret two ways:
#   * a config file present at runtime (found by running the container), and
#   * a credential written then "removed" in a later layer (persists in history).
# See image/Dockerfile.
resource "null_resource" "build_image" {
  triggers = {
    registry   = azurerm_container_registry.acr.name
    image      = local.image_ref
    dockerfile = filemd5("${path.module}/image/Dockerfile")
  }

  provisioner "local-exec" {
    working_dir = "${path.module}/image"
    interpreter = ["/bin/sh", "-c"]

    environment = {
      AZ_CLIENT_ID       = var.client_id
      AZ_CLIENT_SECRET   = var.client_secret
      AZ_TENANT_ID       = var.tenant_id
      AZ_SUBSCRIPTION_ID = var.subscription_id
      ACR_NAME           = azurerm_container_registry.acr.name
      IMAGE_REF          = local.image_ref
    }

    command = <<-EOT
      set -eu
      # Use an isolated CLI profile so the build login does not disturb any
      # interactive `az` session the player has open.
      AZURE_CONFIG_DIR="$(mktemp -d)"
      export AZURE_CONFIG_DIR
      az login --service-principal \
        -u "$AZ_CLIENT_ID" -p "$AZ_CLIENT_SECRET" --tenant "$AZ_TENANT_ID" >/dev/null
      if [ -n "$AZ_SUBSCRIPTION_ID" ]; then
        az account set --subscription "$AZ_SUBSCRIPTION_ID"
      fi
      az acr build --registry "$ACR_NAME" --image "$IMAGE_REF" --file Dockerfile .
      az logout >/dev/null 2>&1 || true
    EOT
  }

  depends_on = [azurerm_container_registry.acr]
}

# "CI/CD artifact cache" — an operations convenience that leaks the registry's
# admin credentials in its resource tags. A Reader on the resource group can
# read tags (`az resource show` / `az tag list`) without any data-plane access,
# which is the foothold for `docker login`.
resource "azurerm_storage_account" "leak" {
  name                     = local.sa_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    app_id                 = var.app_id
    managed                = "terraform"
    purpose                = "cicd-artifact-cache"
    "ci-registry"          = azurerm_container_registry.acr.login_server
    "ci-registry-username" = azurerm_container_registry.acr.admin_username
    "ci-registry-password" = azurerm_container_registry.acr.admin_password
    "ci-image"             = local.image_ref
  }
}

# Attacker identity: a low-privileged user with only Reader on the resource
# group. Reader is enough to discover the registry and read the leaked tags.
data "azuread_client_config" "current" {}

resource "azuread_user" "attacker" {
  user_principal_name   = "attacker-${random_id.suffix.hex}@${var.tenant_domain}"
  display_name          = "Cumulonimbus Attacker ${random_id.suffix.hex}"
  password              = "C@ttack3r!${random_id.suffix.hex}"
  force_password_change = false
}

resource "azurerm_role_assignment" "attacker_reader" {
  scope                = azurerm_resource_group.rg.id
  role_definition_name = "Reader"
  principal_id         = azuread_user.attacker.object_id
}
