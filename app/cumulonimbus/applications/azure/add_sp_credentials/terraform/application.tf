data "azuread_client_config" "current" {}

resource "azuread_application" "group-add-app" {
  display_name = "group-add-app${local.name_suffix_dash}"
  owners       = [data.azuread_client_config.current.object_id]



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

resource "azuread_service_principal" "group-add-sp" {
  application_id               = azuread_application.group-add-app.application_id
  app_role_assignment_required = false
  owners                       = [azuread_user.norightsuser.object_id, data.azuread_client_config.current.object_id]

  feature_tags {
    enterprise = true
    gallery    = true
  }
}

# Grant admin consent for the application permission the SP relies on, the
# app-only way — no `az`/interactive user token required, so it works with the
# service principal Cumulonimbus authenticates as. (The old approach shelled out
# to `az ad app permission admin-consent`, which only works with a signed-in
# user token, not a service principal.) This grants the same Group.ReadWrite.All
# permission to the same SP, so the lab's vulnerability is unchanged.
data "azuread_service_principal" "msgraph" {
  application_id = "00000003-0000-0000-c000-000000000000" # Microsoft Graph
}

resource "azuread_app_role_assignment" "group_readwrite_all" {
  app_role_id         = "62a82d76-70ea-41e2-9197-370581804d09" # Group.ReadWrite.All
  principal_object_id = azuread_service_principal.group-add-sp.object_id
  resource_object_id  = data.azuread_service_principal.msgraph.object_id
}

