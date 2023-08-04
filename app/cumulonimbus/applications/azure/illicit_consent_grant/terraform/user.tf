data "azuread_domains" "aad_domains" {
  only_default = true
}

resource "azuread_user" "norightsuser" {
  user_principal_name = "mriwantconsent@${data.azuread_domains.aad_domains.domains.*.domain_name[0]}"
  display_name        = "Mr Iwant Consent"
  mail_nickname       = "mriwantconsent"
  password            = "IllTakeEverythingYouGiveMe1."
}

resource "azuread_user" "administrator" {
  user_principal_name = "mradminconsent@${data.azuread_domains.aad_domains.domains.*.domain_name[0]}"
  display_name        = "Mr Admin Consent"
  mail_nickname       = "mradminconsent"
  password            = "IllGiveYouEverythingYouWant1."
}


resource "azuread_directory_role" "global_admin" {
  display_name = "Global Administrator"
}

resource "azuread_directory_role_assignment" "global_admin" {
  role_id             = azuread_directory_role.global_admin.template_id
  principal_object_id = azuread_user.administrator.object_id
}
