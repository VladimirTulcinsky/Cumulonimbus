resource "random_integer" "terraform_state_exposure" {
  min = 1
  max = 999999
}

resource "azurerm_resource_group" "terraform_state_exposure" {
  name     = "terraform-state-lab${local.name_suffix_dash}"
  location = var.location
}

# Misconfiguration: Terraform backend storage with public blob access enabled.
# Teams often create this storage account with default (private) settings
# but later enable public access for "convenience" during debugging.
resource "azurerm_storage_account" "tfstate" {
  name                     = "cmlnmbstfstate${random_integer.terraform_state_exposure.result}"
  resource_group_name      = azurerm_resource_group.terraform_state_exposure.name
  location                 = azurerm_resource_group.terraform_state_exposure.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "tfstate" {
  name                  = "tfstate"
  storage_account_name  = azurerm_storage_account.tfstate.name
  # Misconfiguration: container-level public read access on a state backend
  container_access_type = "blob"
}

# Upload a realistic-looking terraform.tfstate file.
# Key teaching point: even outputs marked sensitive=true are stored
# as plaintext in the state file — "sensitive" only suppresses CLI display.
resource "azurerm_storage_blob" "tfstate" {
  name                   = "production/terraform.tfstate"
  storage_account_name   = azurerm_storage_account.tfstate.name
  storage_container_name = azurerm_storage_container.tfstate.name
  type                   = "Block"
  content_type           = "application/json"

  source_content = jsonencode({
    version          = 4
    terraform_version = "1.5.7"
    serial           = 47
    lineage          = "a3f2c1d4-e5b6-7890-abcd-ef1234567890"
    outputs = {
      key_vault_name = {
        value     = "kv-prod-cumulonimbus"
        type      = "string"
        sensitive = false
      }
      service_principal_client_id = {
        value     = "12345678-aaaa-bbbb-cccc-abcdef012345"
        type      = "string"
        sensitive = false
      }
      # The flag: sensitive = true does NOT encrypt the value in state
      service_principal_client_secret = {
        value     = "CUMULONIMBUS{TF_St4t3_S3ns1t1v3_1s_N0t_3ncrypt3d}"
        type      = "string"
        sensitive = true
      }
      storage_account_connection_string = {
        value     = "DefaultEndpointsProtocol=https;AccountName=prodstorage;AccountKey=base64key==;EndpointSuffix=core.windows.net"
        type      = "string"
        sensitive = true
      }
      admin_password = {
        value     = "Pr0dAdm1n!2024#"
        type      = "string"
        sensitive = true
      }
    }
    resources = []
  })
}
