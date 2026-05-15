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
    archive = {
      source  = "hashicorp/archive"
      version = "2.4.0"
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


resource "azurerm_resource_provider_registration" "microsoft_web" {
  name = "Microsoft.Web"
}
