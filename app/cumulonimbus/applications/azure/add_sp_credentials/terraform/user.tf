
resource "azuread_user" "norightsuser" {
  user_principal_name = "norightsuser${local.name_suffix_dash}@${var.tenant_domain}"
  display_name        = "No Rights User${local.name_suffix_dash}"
  mail_nickname       = "norightsuser${local.name_suffix_dash}"
  password            = "IHaveNoRights1."
}

resource "azuread_user" "group_owner" {
  user_principal_name = "cred-group-owner${local.name_suffix_dash}@${var.tenant_domain}"
  display_name        = "Cred Group Owner${local.name_suffix_dash}"
  mail_nickname       = "cred-group-owner${local.name_suffix_dash}"
  password            = "JustBecauseAgroupNeedsAnOwnerHehe1."
}

resource "azuread_group" "administrators" {
  display_name     = "cred-administrators${local.name_suffix_dash}"
  mail_nickname    = "cred-administrators${local.name_suffix_dash}"
  description      = "This group should have the Global Admin role assigned, but this required a P1 license."
  security_enabled = true

  owners = [
    azuread_user.group_owner.object_id
  ]
}

