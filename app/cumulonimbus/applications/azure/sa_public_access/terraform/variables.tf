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
  default     = "0.0.0.0/0"
}

variable "app_id" {
  type        = string
  description = "Name of the application, here: ec2_ssrf"
  default     = "ec2_ssrf"
}
