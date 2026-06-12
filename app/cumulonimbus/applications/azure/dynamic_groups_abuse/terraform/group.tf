# Dynamic group: anyone whose department attribute is "Security" is automatically
# a member. Members inherit Key Vault Secrets User on the flag vault.
resource "azuread_group" "security_team" {
  display_name     = "Security Team${local.name_suffix_dash}"
  description      = "Members of the internal security department"
  security_enabled = true
  types            = ["DynamicMembership"]

  dynamic_membership {
    enabled = true
    rule    = "user.department -eq \"Security\""
  }
}

resource "azurerm_role_assignment" "group_kv_reader" {
  scope                = azurerm_key_vault.flag.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azuread_group.security_team.object_id
}
