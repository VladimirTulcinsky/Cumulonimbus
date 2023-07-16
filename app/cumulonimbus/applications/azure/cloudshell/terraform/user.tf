data "azuread_domains" "aad_domains" {
  only_default = true
}

resource "azuread_user" "victim" {
  user_principal_name = "noherback@${data.azuread_domains.aad_domains.domains.*.domain_name[0]}"
  display_name        = "Noher Back"
  mail_nickname       = "nback"
  password            = "IDontLikeIAMPfff1."
}

resource "azurerm_role_assignment" "noherback" {
  scope                = azurerm_resource_group.iam_cs.id
  role_definition_name = "Contributor"
  principal_id         = azuread_user.victim.id
}

resource "azurerm_role_definition" "vm_admin" {
  name        = "restricted_vm_user_login"
  scope       = azurerm_resource_group.vm_cs.id
  description = "Restricted role to avoid password resets"

  permissions {
    actions = ["Microsoft.Network/publicIPAddresses/read",
      "Microsoft.Network/virtualNetworks/read",
      "Microsoft.Network/loadBalancers/read",
      "Microsoft.Network/networkInterfaces/read",
    "Microsoft.Compute/virtualMachines/*/read"]

    not_actions = ["Microsoft.Resources/deployments/read",
      "Microsoft.Resources/deployments/write",
      "Microsoft.Resources/deployments/delete",
      "Microsoft.Resources/deployments/cancel/action",
      "Microsoft.Resources/deployments/validate/action",
      "Microsoft.Resources/deployments/whatIf/action",
      "Microsoft.Resources/deployments/exportTemplate/action",
      "Microsoft.Resources/deployments/operations/read",
      "Microsoft.Resources/deployments/operationstatuses/read",
      "Microsoft.Resources/deploymentScripts/read",
      "Microsoft.Resources/deploymentScripts/write",
      "Microsoft.Resources/deploymentScripts/delete",
      "Microsoft.Resources/deploymentScripts/logs/read",
      "Microsoft.Resources/deploymentStacks/read",
      "Microsoft.Resources/deploymentStacks/write",
      "Microsoft.Resources/deploymentStacks/delete",
      "Microsoft.Compute/virtualMachines/extensions/read", // doesn't work don't know why
      "Microsoft.Compute/locations/publishers/artifacttypes/types/read",
      "Microsoft.Compute/locations/publishers/artifacttypes/types/versions/read"
    ]

    data_actions = ["Microsoft.Compute/virtualMachines/login/action"]
  }

  assignable_scopes = [azurerm_resource_group.vm_cs.id]

}

resource "azurerm_role_assignment" "vm_admin" {
  scope              = azurerm_resource_group.vm_cs.id
  role_definition_id = azurerm_role_definition.vm_admin.role_definition_resource_id
  principal_id       = azuread_user.victim.id
}


