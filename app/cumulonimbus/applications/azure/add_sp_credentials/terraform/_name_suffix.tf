# Per-player namespacing.
#
# The Cumulonimbus CLI passes name_suffix from the player's "session name" so
# that several people sharing ONE set of cloud credentials in the same
# tenant/account do not collide on resource names. It is empty by default,
# which preserves the original single-tenant behaviour.
variable "name_suffix" {
  type        = string
  description = "Optional per-player identifier appended to collision-prone resource names."
  default     = ""
}

locals {
  # "-alice" when a session name is set, otherwise "" (default behaviour unchanged).
  name_suffix_dash = var.name_suffix != "" ? "-${var.name_suffix}" : ""
}
