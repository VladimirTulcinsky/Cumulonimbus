resource "random_integer" "arm_deployment_history" {
  min = 1
  max = 999999
}

resource "azurerm_resource_group" "arm_deployment_history" {
  name     = "arm-deployment-history-lab"
  location = var.location
}

# A minimal ARM template deployment that passes the flag as a plain 'string'
# parameter instead of 'secureString'.
# Misconfiguration: using string instead of secureString causes the value to
# appear in plaintext in az deployment group show output, visible to any
# identity with Microsoft.Resources/deployments/read (included in Reader).
resource "azurerm_resource_group_template_deployment" "app_infra" {
  name                = "app-infra-v1"
  resource_group_name = azurerm_resource_group.arm_deployment_history.name
  deployment_mode     = "Incremental"

  parameters_content = jsonencode({
    # Would be "secureString" type in a safe template — string exposes it in history
    adminApiKey = { value = "CUMULONIMBUS{4RM_D3pl0yment_H1st0ry_Pl41nt3xt}" }
    environment = { value = "production" }
    appName     = { value = "cumulonimbus-portal-${random_integer.arm_deployment_history.result}" }
  })

  template_content = jsonencode({
    "$schema"        = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#"
    contentVersion   = "1.0.0.0"
    parameters = {
      adminApiKey = {
        # Misconfiguration: should be "secureString" — secureString values are
        # masked as "[secure]" in deployment history; string values are plaintext.
        type        = "string"
        metadata    = { description = "Admin API key for the application" }
      }
      environment = { type = "string" }
      appName     = { type = "string" }
    }
    resources = [
      {
        type       = "Microsoft.Storage/storageAccounts"
        apiVersion = "2022-09-01"
        name       = "cmlnmbsarm${random_integer.arm_deployment_history.result}"
        location   = "[resourceGroup().location]"
        sku        = { name = "Standard_LRS" }
        kind       = "StorageV2"
        tags = {
          environment = "[parameters('environment')]"
          app         = "[parameters('appName')]"
        }
      }
    ]
    outputs = {
      storageAccountName = {
        type  = "string"
        value = "cmlnmbsarm${random_integer.arm_deployment_history.result}"
      }
    }
  })
}

# ── Attacker user: Reader on the resource group ───────────────────────────────


resource "random_password" "attacker" {
  length           = 16
  special          = true
  override_special = "!@#"
  min_upper        = 2
  min_numeric      = 2
}

resource "azuread_user" "attacker" {
  user_principal_name   = "arm-auditor@${var.tenant_domain}"
  display_name          = "ARM Auditor"
  mail_nickname         = "arm-auditor"
  password              = random_password.attacker.result
  force_password_change = false
}

resource "azurerm_role_assignment" "attacker_reader" {
  scope                = azurerm_resource_group.arm_deployment_history.id
  role_definition_name = "Reader"
  principal_id         = azuread_user.attacker.object_id
}
