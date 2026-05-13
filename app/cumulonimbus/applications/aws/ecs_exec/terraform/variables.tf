variable "shared_credentials_files" {
  type    = string
  default = "~/.aws/credentials"
}

variable "shared_config_files" {
  type    = string
  default = "~/.aws/config"
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
  default = "ecs_exec"
}
