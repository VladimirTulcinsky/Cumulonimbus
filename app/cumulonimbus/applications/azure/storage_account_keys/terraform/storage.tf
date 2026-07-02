resource "random_id" "suffix" {
  byte_length = 4
}

locals {
  rg_name      = "cumulonimbus-${var.app_id}-${random_id.suffix.hex}"
  storage_name = "cnimbus${random_id.suffix.hex}"
}

resource "azurerm_resource_group" "rg" {
  name     = local.rg_name
  location = var.location
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "azurerm_storage_account" "sa" {
  name                     = local.storage_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  # Public network access on, but no anonymous blob access
  allow_nested_items_to_be_public = false
  public_network_access_enabled   = true

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "azurerm_storage_container" "secrets" {
  name                  = "internal-secrets"
  storage_account_name  = azurerm_storage_account.sa.name
  container_access_type = "private"
}

resource "azurerm_storage_blob" "flag" {
  name                   = "credentials.txt"
  storage_account_name   = azurerm_storage_account.sa.name
  storage_container_name = azurerm_storage_container.secrets.name
  type                   = "Block"
  source_content         = "CUMULONIMBUS{St0r4g3_Acc0unt_K3ys_Byp4ss_RBAC}"
}

# Attacker has Storage Account Contributor (control plane) — can list account keys
# Storage Account Contributor does NOT include Storage Blob Data Reader (data plane)
# BUT listing keys provides full storage access, bypassing RBAC data plane controls
data "azuread_client_config" "current" {}

resource "azuread_user" "attacker" {
  user_principal_name   = "attacker-${random_id.suffix.hex}@${var.tenant_domain}"
  display_name          = "Cumulonimbus Attacker ${random_id.suffix.hex}"
  password              = "C@ttack3r!${random_id.suffix.hex}"
  force_password_change = false
}

resource "azurerm_role_assignment" "attacker_sa_contributor" {
  scope                = azurerm_storage_account.sa.id
  role_definition_name = "Storage Account Contributor"
  principal_id         = azuread_user.attacker.object_id
}
