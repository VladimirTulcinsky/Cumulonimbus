data "azuread_domains" "aad_domains" {
  only_default = true
}

resource "azuread_user" "attacker" {
  user_principal_name = "ska_attacker@${data.azuread_domains.aad_domains.domains.*.domain_name[0]}"
  display_name        = "Ska Attacker"
  password            = "IWillAttackSKA1."
}

resource "azurerm_role_assignment" "reader" {
  scope                = azurerm_resource_group.ska_sa.id
  role_definition_name = "Reader"
  principal_id         = azuread_user.attacker.id
}

resource "azurerm_role_assignment" "sa_contributor" {
  scope                = azurerm_storage_account.ska_sa.id
  role_definition_name = "Storage Account Contributor"
  principal_id         = azuread_user.attacker.id
}


