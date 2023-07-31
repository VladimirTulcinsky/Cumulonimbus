data "azuread_domains" "aad_domains" {
  only_default = true
}

resource "azuread_user" "administrator" {
  user_principal_name = "almightyadmin@${data.azuread_domains.aad_domains.domains.*.domain_name[0]}"
  display_name        = "Almighty Admin"
  mail_nickname       = "aadmin"
  password            = "FocIHaveToFindAnotherP@sswd1."
}

resource "azuread_user" "grouper" {
  user_principal_name = "grouper@${data.azuread_domains.aad_domains.domains.*.domain_name[0]}"
  display_name        = "Grouper Phish"
  mail_nickname       = "gphish"
  password            = "ICanAddYouToAGroup1Hehe."
}


resource "azuread_directory_role" "groups_admin" {
  display_name = "Groups Administrator"
}

resource "azuread_directory_role_assignment" "groups_admin" {
  role_id             = azuread_directory_role.groups_admin.template_id
  principal_object_id = azuread_user.grouper.object_id
}
