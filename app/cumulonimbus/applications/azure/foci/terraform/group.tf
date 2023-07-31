resource "azuread_group" "administrators" {
  display_name       = "Almighty Administrators"
  owners             = [azuread_user.administrator.object_id]
  security_enabled   = true
  assignable_to_role = true
}

resource "azuread_directory_role" "global_admin" {
  display_name = "Global Administrator"
}

resource "azuread_directory_role_assignment" "global_admin" {
  role_id             = azuread_directory_role.global_admin.template_id
  principal_object_id = azuread_group.administrators.object_id
}


