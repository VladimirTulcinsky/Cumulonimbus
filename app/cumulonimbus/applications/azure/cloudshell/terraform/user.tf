data "azuread_domains" "aad_domains" {
  only_default = true
}

resource "azuread_user" "victim" {
  user_principal_name = "noherback@${data.azuread_domains.aad_domains.domains.*.domain_name[0]}"
  display_name        = "Noher Back"
  mail_nickname       = "nback"
  password            = "IDontLikeIAMPfff1."
}

resource "azurerm_role_assignment" "noherback" {
  scope                = azurerm_resource_group.iam_cs.id
  role_definition_name = "Contributor"
  principal_id         = azuread_user.victim.id
}


