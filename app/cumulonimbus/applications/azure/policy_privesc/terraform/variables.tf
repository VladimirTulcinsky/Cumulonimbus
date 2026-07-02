variable "client_id" {
  type        = string
  description = "Service Principal's Client ID for Azure authentication"
  default     = ""
}

variable "client_secret" {
  type        = string
  description = "Service Principal's Secret for Azure authentication"
  default     = ""
}

variable "tenant_id" {
  type        = string
  description = "Tenant ID for Azure authentication"
  default     = ""

  validation {
    condition     = var.tenant_id == "" || can(regex("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", var.tenant_id))
    error_message = "tenant_id must be a valid UUID or empty string."
  }
}

variable "subscription_id" {
  type        = string
  description = "Subscription ID for Azure authentication"
  default     = ""

  validation {
    condition     = var.subscription_id == "" || can(regex("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", var.subscription_id))
    error_message = "subscription_id must be a valid UUID or empty string."
  }
}

variable "attacker_public_ip" {
  type        = string
  description = "Attacker public IP address for whitelisting purposes"
  default     = "0.0.0.0"

  validation {
    condition     = can(regex("^(\\d{1,3}\\.){3}\\d{1,3}$", var.attacker_public_ip))
    error_message = "attacker_public_ip must be a valid IPv4 address."
  }
}

locals {
  attacker_public_ip_cidr = var.attacker_public_ip == "0.0.0.0" ? "0.0.0.0/0" : "${var.attacker_public_ip}/32"
}

variable "app_id" {
  type        = string
  description = "Name of the application"
  default     = "policy_privesc"
}

variable "app_name" {
  type        = string
  description = "Application name used in resource naming"
  default     = "cumulonimbus"
}

variable "tenant_domain" {
  type        = string
  description = "Primary domain of the Azure AD tenant (e.g. contoso.onmicrosoft.com). Pass --tenant-domain when authenticating."

  validation {
    condition     = length(var.tenant_domain) > 0
    error_message = "tenant_domain is required for this lab. Re-authenticate: cnimbus azure authenticate ... --tenant-domain <domain>"
  }
}

variable "location" {
  type        = string
  description = "Azure region to deploy resources to"
  default     = "West Europe"
}
