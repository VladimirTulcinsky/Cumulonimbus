variable "client_id" {
  type    = string
  default = ""
}

variable "client_secret" {
  type    = string
  default = ""
}

variable "tenant_id" {
  type    = string
  default = ""

  validation {
    condition     = var.tenant_id == "" || can(regex("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", var.tenant_id))
    error_message = "tenant_id must be a valid UUID or empty string."
  }
}

variable "subscription_id" {
  type    = string
  default = ""

  validation {
    condition     = var.subscription_id == "" || can(regex("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", var.subscription_id))
    error_message = "subscription_id must be a valid UUID or empty string."
  }
}

variable "attacker_public_ip" {
  type    = string
  default = "0.0.0.0"

  validation {
    condition     = can(regex("^(\\d{1,3}\\.){3}\\d{1,3}$", var.attacker_public_ip))
    error_message = "attacker_public_ip must be a valid IPv4 address."
  }
}

locals {
  attacker_public_ip_cidr = var.attacker_public_ip == "0.0.0.0" ? "0.0.0.0/0" : "${var.attacker_public_ip}/32"
}

variable "app_id" {
  type    = string
  default = "gatekeeper_chain_2"
}

variable "app_name" {
  type    = string
  default = "cumulonimbus"
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

# Container Apps run on a managed AKS backend that can hit regional capacity
# limits (AKSCapacityHeavyUsage). This lets the Container App stage (its
# environment + Log Analytics workspace) be placed in a different region from
# the rest of the lab WITHOUT moving everything. Empty = use var.location.
# Override it without touching the CLI:  export TF_VAR_container_app_location="North Europe"
variable "container_app_location" {
  type        = string
  description = "Region for the Container App environment (empty = same as var.location). Set via TF_VAR_container_app_location to dodge AKS capacity errors."
  default     = ""
}
