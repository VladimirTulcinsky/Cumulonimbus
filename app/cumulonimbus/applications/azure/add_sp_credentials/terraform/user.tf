data "azuread_domains" "aad_domains" {
  only_default = true
}

resource "azuread_user" "norightsuser" {
  user_principal_name = "norightsuser@${data.azuread_domains.aad_domains.domains.*.domain_name[0]}"
  display_name        = "No Rights User"
  mail_nickname       = "norightsuser"
  password            = "IHaveNoRights1."
}

resource "azuread_user" "group_owner" {
  user_principal_name = "cred-group-owner@${data.azuread_domains.aad_domains.domains.*.domain_name[0]}"
  display_name        = "Cred Group Owner"
  mail_nickname       = "cred-group-owner"
  password            = "JustBecauseAgroupNeedsAnOwnerHehe1."
}

resource "azuread_group" "administrators" {
  display_name     = "cred-administrators"
  mail_nickname    = "cred-administrators"
  description      = "This group should have the Global Admin role assigned, but this required a P1 license."
  security_enabled = true

  owners = [
    azuread_user.group_owner.object_id
  ]
}

