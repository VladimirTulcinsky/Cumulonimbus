terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.51.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.4.3"
    }
    cloudinit = {
      source  = "hashicorp/cloudinit"
      version = "2.2.0"
    }
  }
}

provider "aws" {
  region                   = "eu-west-1"
  shared_credentials_files = [var.shared_credentials_files]
  shared_config_files      = [var.shared_config_files]
  profile                  = "cumulonimbus"
}




