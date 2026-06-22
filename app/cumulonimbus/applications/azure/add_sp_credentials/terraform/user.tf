
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
  description      = "This group should have the Global Admin role assigned, but that required a P1 license. Instead it was granted the 'Key Vault Secrets User' role on the team Key Vault, so members can read the vault's secrets."
  security_enabled = true

  owners = [
    azuread_user.group_owner.object_id
  ]
}

