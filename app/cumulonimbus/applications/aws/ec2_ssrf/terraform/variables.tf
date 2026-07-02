variable "shared_credentials_files" {
  type        = string
  description = "Path to the AWS credentials file, is replaced by ENV variable in Docker container"
  default     = "~/.aws/credentials"
}

variable "shared_config_files" {
  type        = string
  description = "Path to the AWS config file, is replaced by ENV variable in Docker container"
  default     = "~/.aws/config"
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

// had to find a hack,  causes issues on destroy, see: https://github.com/hashicorp/terraform/issues/23552#issuecomment-1584824629
locals {
  attacker_public_ip_cidr = var.attacker_public_ip == "0.0.0.0" ? "0.0.0.0/0" : "${var.attacker_public_ip}/32"
}

variable "app_id" {
  type        = string
  description = "Name of the application, here: ec2_ssrf"
  default     = "ec2_ssrf"
}

variable "region" {
  type        = string
  description = "AWS region to deploy resources to"
  default     = "eu-west-1"
}
