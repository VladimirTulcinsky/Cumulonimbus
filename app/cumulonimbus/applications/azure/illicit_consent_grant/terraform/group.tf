resource "azuread_group" "administrators" {
  display_name     = "cs-administrators"
  description      = "This group should have the Global Admin role assigned, but this required a P1 license."
  owners           = [azuread_user.administrator.object_id]
  security_enabled = true
}



