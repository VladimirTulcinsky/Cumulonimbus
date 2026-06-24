###############################################################################
# Stage 1 — a private Azure Container Registry hosting a custom image whose
# layers/filesystem hide two plaintext secrets. The gatekeeper grants the
# attacker AcrPull (+ Reader so `az acr login` can resolve the registry) in
# exchange for the bootstrap flag; the player then pulls and dissects the image.
###############################################################################
resource "azurerm_container_registry" "acr" {
  name                = local.acr_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = false

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# Build the scenario image server-side with ACR Tasks (`az acr build`) — no local
# Docker daemon needed. The deployer service principal authenticates and builds
# the image in image/Dockerfile.
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
