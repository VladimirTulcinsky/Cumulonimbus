
resource "azuread_user" "norightsuser" {
  user_principal_name = "mriwantconsent${local.name_suffix_dash}@${var.tenant_domain}"
  display_name        = "Mr Iwant Consent${local.name_suffix_dash}"
  mail_nickname       = "mriwantconsent${local.name_suffix_dash}"
  password            = "IllTakeEverythingYouGiveMe1."
}

resource "azuread_user" "administrator" {
  user_principal_name = "mradminconsent${local.name_suffix_dash}@${var.tenant_domain}"
  display_name        = "Mr Admin Consent${local.name_suffix_dash}"
  mail_nickname       = "mradminconsent${local.name_suffix_dash}"
  password            = "IllGiveYouEverythingYouWant1."
}


resource "azuread_directory_role" "global_admin" {
  display_name = "Global Administrator"
}

resource "azuread_directory_role_assignment" "global_admin" {
  role_id             = azuread_directory_role.global_admin.template_id
  principal_object_id = azuread_user.administrator.object_id
}
