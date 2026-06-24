terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.116"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "2.40.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.5.1"
    }
    null = {
      source  = "hashicorp/null"
      version = "3.2.1"
    }
  }
}

provider "azurerm" {
  features {}

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

# NOTE: this lab does NOT manage the resource-provider registration.
# `azurerm_resource_provider_registration` always tries to *create* the
# registration and fails if Microsoft.ContainerRegistry is already registered
# on the subscription (the common case). On a brand-new subscription, register
# it once with: az provider register --namespace Microsoft.ContainerRegistry --wait
