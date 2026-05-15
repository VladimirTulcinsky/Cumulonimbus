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
  features {}

  skip_provider_registration    = true
  resource_providers_to_register = []

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


resource "azurerm_resource_provider_registration" "microsoft_web" {
  name = "Microsoft.Web"
}

resource "azurerm_resource_provider_registration" "microsoft_keyvault" {
  name = "Microsoft.KeyVault"
}
