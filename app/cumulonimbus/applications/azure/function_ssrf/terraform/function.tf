resource "random_integer" "function_ssrf" {
  min = 1
  max = 999999
}

resource "azurerm_resource_group" "function_ssrf" {
  name     = "function-ssrf-lab"
  location = "West Europe"
}

# ── Flag storage (private, accessible only via the Function App MI) ───────────

resource "azurerm_storage_account" "flag" {
  name                     = "cmlnmbsflag${random_integer.function_ssrf.result}"
  resource_group_name      = azurerm_resource_group.function_ssrf.name
  location                 = azurerm_resource_group.function_ssrf.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "secrets" {
  name                  = "secrets"
  storage_account_name  = azurerm_storage_account.flag.name
  container_access_type = "private"
}

resource "azurerm_storage_blob" "flag" {
  name                   = "flag.txt"
  storage_account_name   = azurerm_storage_account.flag.name
  storage_container_name = azurerm_storage_container.secrets.name
  type                   = "Block"
  source_content         = "CUMULONIMBUS{Funct10n_SSRF_1MDS_T0k3n}\n"
}

# ── Storage for Function App infrastructure + code package ────────────────────

resource "azurerm_storage_account" "functions" {
  name                     = "cmlnmbsfunc${random_integer.function_ssrf.result}"
  resource_group_name      = azurerm_resource_group.function_ssrf.name
  location                 = azurerm_resource_group.function_ssrf.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "deploy" {
  name                  = "deploy"
  storage_account_name  = azurerm_storage_account.functions.name
  container_access_type = "private"
}

# Build the function code zip in-place
data "archive_file" "function_package" {
  type        = "zip"
  output_path = "${path.module}/function_app.zip"

  source {
    filename = "fetch/__init__.py"
    content  = <<-PY
      import urllib.request
      import azure.functions as func

      def main(req: func.HttpRequest) -> func.HttpResponse:
          url = req.params.get("url")
          if not url:
              return func.HttpResponse("Missing ?url= parameter", status_code=400)
          try:
              with urllib.request.urlopen(url, timeout=10) as r:
                  body = r.read().decode("utf-8", errors="replace")
              return func.HttpResponse(body, status_code=200)
          except Exception as e:
              return func.HttpResponse(f"Error: {e}", status_code=500)
    PY
  }

  source {
    filename = "fetch/function.json"
    content  = jsonencode({
      bindings = [
        {
          authLevel = "anonymous"
          type      = "httpTrigger"
          direction = "in"
          name      = "req"
          methods   = ["get", "post"]
        },
        {
          type      = "http"
          direction = "out"
          name      = "$return"
        }
      ]
    })
  }

  source {
    filename = "host.json"
    content  = jsonencode({ version = "2.0" })
  }

  source {
    filename = "requirements.txt"
    content  = "azure-functions\n"
  }
}

resource "azurerm_storage_blob" "function_package" {
  name                   = "function_app.zip"
  storage_account_name   = azurerm_storage_account.functions.name
  storage_container_name = azurerm_storage_container.deploy.name
  type                   = "Block"
  source                 = data.archive_file.function_package.output_path
  content_md5            = data.archive_file.function_package.output_md5
}

data "azurerm_storage_account_sas" "deploy" {
  connection_string = azurerm_storage_account.functions.primary_connection_string
  https_only        = true
  signed_version    = "2019-12-12"

  resource_types {
    service   = false
    container = false
    object    = true
  }

  services {
    blob  = true
    queue = false
    table = false
    file  = false
  }

  start  = "2024-01-01T00:00:00Z"
  expiry = "2030-01-01T00:00:00Z"

  permissions {
    read    = true
    write   = false
    delete  = false
    list    = false
    add     = false
    create  = false
    update  = false
    process = false
    tag     = false
    filter  = false
  }
}

# ── App Service Plan (Consumption / serverless) ───────────────────────────────

resource "azurerm_service_plan" "function_ssrf" {
  name                = "asp-ssrf-${random_integer.function_ssrf.result}"
  location            = azurerm_resource_group.function_ssrf.location
  resource_group_name = azurerm_resource_group.function_ssrf.name
  os_type             = "Linux"
  sku_name            = "Y1"
}

# ── Function App with system-assigned managed identity ────────────────────────

resource "azurerm_linux_function_app" "function_ssrf" {
  name                       = "fn-ssrf-${random_integer.function_ssrf.result}"
  location                   = azurerm_resource_group.function_ssrf.location
  resource_group_name        = azurerm_resource_group.function_ssrf.name
  service_plan_id            = azurerm_service_plan.function_ssrf.id
  storage_account_name       = azurerm_storage_account.functions.name
  storage_account_access_key = azurerm_storage_account.functions.primary_access_key

  identity {
    type = "SystemAssigned"
  }

  site_config {
    application_stack {
      python_version = "3.9"
    }
  }

  app_settings = {
    FUNCTIONS_WORKER_RUNTIME = "python"
    # Package URL — the function fetches any caller-supplied ?url= without sanitisation
    WEBSITE_RUN_FROM_PACKAGE = "${azurerm_storage_blob.function_package.url}${data.azurerm_storage_account_sas.deploy.sas}"
  }
}

# Grant the Function App's MI Storage Blob Data Reader on the flag storage account
resource "azurerm_role_assignment" "func_storage_reader" {
  scope                = azurerm_storage_account.flag.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = azurerm_linux_function_app.function_ssrf.identity[0].principal_id
}
