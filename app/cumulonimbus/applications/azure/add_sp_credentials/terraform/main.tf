terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.116"
    }

    random = {
      source  = "hashicorp/random"
      version = "3.5.1"
    }

    azuread = {
      source  = "hashicorp/azuread"
      version = "2.40.0"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }

  skip_provider_registration = true

  subscription_id = var.subscription_id
  client_id       = var.client_id
  client_secret   = var.client_secret
  tenant_id       = var.tenant_id
}

provider "azuread" {
  client_id     = var.client_id
  client_secret = var.client_secret
  tenant_id     = var.tenant_id
}

data "azurerm_client_config" "current" {}

resource "random_integer" "suffix" {
  min = 10000
  max = 99999
}

# Resource group that hosts the Key Vault the privesc ultimately unlocks.
resource "azurerm_resource_group" "rg" {
  name     = "cumulonimbus-add-sp${local.name_suffix_dash}-${random_integer.suffix.result}"
  location = var.location
}
