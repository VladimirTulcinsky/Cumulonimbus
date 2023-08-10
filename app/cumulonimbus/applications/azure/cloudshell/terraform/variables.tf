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
}

variable "subscription_id" {
  type        = string
  description = "Tenant ID for Azure authentication"
  default     = ""
}

variable "attacker_public_ip" {
  type        = string
  description = "Attacker public IP address for whitelisting purposes"
  default     = "0.0.0.0"
}

// had to find a hack,  causes issues on destroy, see: https://github.com/hashicorp/terraform/issues/23552#issuecomment-1584824629
locals {
  attacker_public_ip_cidr = var.attacker_public_ip == "0.0.0.0" ? "0.0.0.0/0" : "${var.attacker_public_ip}/32"
}

variable "app_id" {
  type        = string
  description = "Name of the application, here: cloudshell"
  default     = "cloudshell"
}

variable "app_name" {
  type        = string
  description = "Name of the application that will be used in the resource names and complemented with a random number"
  default     = "cumulonimbus"
}
