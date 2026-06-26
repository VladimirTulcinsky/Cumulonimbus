terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.116"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.40"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.5.1"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.9"
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

# NOTE: this lab does NOT manage resource-provider registrations. azurerm's
# `azurerm_resource_provider_registration` always tries to *create* the
# registration and fails if the provider is already registered on the
# subscription (the common case). The providers used here
# (Microsoft.AppConfiguration, ContainerInstance, ApiManagement, DataFactory,
# microsoft.insights, KeyVault, Storage) are registered on any subscription
# that has used these services. On a brand-new subscription, register the few
# that are missing once with, e.g.:
#   az provider register --namespace Microsoft.ApiManagement --wait

