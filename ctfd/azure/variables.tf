variable "location" {
  type        = string
  description = "Azure region to deploy the CTFd VM to."
  default     = "West Europe"
}

variable "vm_size" {
  type        = string
  description = "VM size for the CTFd host. Default is widely available; if you hit SkuNotAvailable, try another (e.g. Standard_B2ms, Standard_D2as_v5) or another region."
  default     = "Standard_D2s_v3"
}

variable "admin_username" {
  type        = string
  description = "Linux admin username for SSH."
  default     = "ctfdadmin"
}

variable "admin_ssh_public_key" {
  type        = string
  description = "SSH public key for the admin user (e.g. file(\"~/.ssh/id_rsa.pub\"))."
}

variable "ssh_allowed_cidr" {
  type        = string
  description = "CIDR allowed to SSH (port 22). Restrict to your own IP; 0.0.0.0/0 exposes SSH to the internet (key-only auth still applies)."
  default     = "0.0.0.0/0"
}

variable "player_allowed_cidr" {
  type        = string
  description = "CIDR allowed to reach the CTFd scoreboard (port 8001). Players need this; 0.0.0.0/0 makes it world-reachable."
  default     = "0.0.0.0/0"
}

variable "ctfd_admin_password" {
  type        = string
  description = "CTFd admin account password (username: admin). Change this from the default."
  default     = "cumulonimbus"
  sensitive   = true
}

variable "repo_url" {
  type        = string
  description = "Git repository to clone on the VM (must contain the ctfd/ directory)."
  default     = "https://github.com/VladimirTulcinsky/Cumulonimbus.git"
}

variable "git_ref" {
  type        = string
  description = "Branch or tag to clone (determines which challenges/points are seeded)."
  default     = "main"
}
