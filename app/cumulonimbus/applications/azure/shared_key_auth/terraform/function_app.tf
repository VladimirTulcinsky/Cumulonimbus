resource "azurerm_service_plan" "ska_asp" {
  name                = "aspska${var.app_name}${random_integer.ska.result}"
  resource_group_name = azurerm_resource_group.ska_sa.name
  location            = azurerm_resource_group.ska_sa.location
  os_type             = "Windows"
  sku_name            = "Y1"
}

resource "azurerm_windows_function_app" "ska_fapp" {
  name                = "fappska${var.app_name}${random_integer.ska.result}"
  resource_group_name = azurerm_resource_group.ska_sa.name
  location            = azurerm_resource_group.ska_sa.location

  storage_account_name       = azurerm_storage_account.ska_sa.name
  storage_account_access_key = azurerm_storage_account.ska_sa.primary_access_key
  service_plan_id            = azurerm_service_plan.ska_asp.id

  site_config {
    cors {
      allowed_origins = ["https://portal.azure.com"]
    }

    /*     ip_restriction {
      ip_address = "${var.attacker_public_ip}/32"
      action     = "Allow"
      name       = "allow_only_attacker"
    } */

    application_stack {
      node_version = "~18"

    }
  }

  app_settings = {
    KEY_VAULT_NAME                 = azurerm_key_vault.ska_kv.name
    SECRET_NAME                    = azurerm_key_vault_secret.fapp-secret.name
    functions_extension_version    = "~4"
    SCM_DO_BUILD_DURING_DEPLOYMENT = true
  }

  identity {
    type = "SystemAssigned"
  }




}

resource "azurerm_function_app_function" "function" {
  name            = "fapp"
  function_app_id = azurerm_windows_function_app.ska_fapp.id
  language        = "Javascript"

  file {
    name    = "fapp.js"
    content = file("./../files/fapp.js")
  }

  config_json = jsonencode({
    "bindings" = [
      {
        "authLevel" = "anonymous"
        "direction" = "in"
        "methods" = [
          "get",
          "post"
        ]
        "name" = "req"
        "type" = "httpTrigger"
      },
      {
        "direction" = "out"
        "name"      = "res"
        "type"      = "http"
      },
    ]
  })
}


resource "azurerm_role_assignment" "kv_secrets_user" {
  scope                = azurerm_key_vault.ska_kv.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_windows_function_app.ska_fapp.identity[0].principal_id
}
