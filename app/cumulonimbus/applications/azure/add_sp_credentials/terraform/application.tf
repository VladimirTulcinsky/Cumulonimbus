resource "azuread_application" "group-add-app" {
  display_name    = "group-add-app-test"
  identifier_uris = ["api://group-add-app"]
  owners          = [azuread_user.norightsuser.object_id]



  required_resource_access {
    resource_app_id = "00000003-0000-0000-c000-000000000000" # Microsoft Graph

    resource_access {
      id   = "62a82d76-70ea-41e2-9197-370581804d09" # Group.ReadWrite.All
      type = "Role"
    }

    resource_access {
      id   = "e1fe6dd8-ba31-4d61-89e7-88639da4683d" # User.ReadWrite
      type = "Scope"
    }
  }
}

// Had to use this hack as admin consent doesn't exist in Terraform (yet)
resource "null_resource" "aad_admin_consent" {
  triggers = merge(
    [for app in azuread_application.group-add-app.required_resource_access :
      { for role in app.resource_access :
        join("_", [app.resource_app_id, role.id]) => role.type
      }
    ]...
  )

  provisioner "local-exec" {
    command = "sleep 30 && az ad app permission admin-consent --id ${azuread_application.group-add-app.application_id}"
  }
}

