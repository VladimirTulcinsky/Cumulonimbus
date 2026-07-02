resource "random_password" "attacker" {
  length           = 16
  special          = true
  override_special = "!@#"
  min_upper        = 2
  min_numeric      = 2
}

resource "azuread_user" "attacker" {
  user_principal_name   = "dga-attacker${local.name_suffix_dash}@${var.tenant_domain}"
  display_name          = "DGA Attacker${local.name_suffix_dash}"
  mail_nickname         = "dga-attacker${local.name_suffix_dash}"
  password              = random_password.attacker.result
  force_password_change = false
}

# Misconfiguration: attacker has User Account Administrator, which allows
# modifying other users' attributes — including their own department field.
data "azuread_directory_role" "user_account_admin" {
  display_name = "User Account Administrator"
}

resource "azuread_directory_role_assignment" "attacker_user_admin" {
  role_id             = data.azuread_directory_role.user_account_admin.template_id
  principal_object_id = azuread_user.attacker.object_id
}
