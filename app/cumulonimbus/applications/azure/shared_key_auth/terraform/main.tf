terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.65.0"
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
  features {}

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

resource "random_integer" "ska" {
  min = 1
  max = 999999
}
