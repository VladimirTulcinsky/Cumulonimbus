resource "random_integer" "automation_account" {
  min = 1
  max = 999999
}

resource "azurerm_resource_group" "automation_account" {
  name     = "automation-account-lab${local.name_suffix_dash}"
  location = var.location

  depends_on = [azurerm_resource_provider_registration.microsoft_automation]
}

# ── Flag storage ──────────────────────────────────────────────────────────────

resource "azurerm_storage_account" "flag" {
  name                     = "cmlnmbsauto${random_integer.automation_account.result}"
  resource_group_name      = azurerm_resource_group.automation_account.name
  location                 = azurerm_resource_group.automation_account.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
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
  source_content         = "CUMULONIMBUS{Aut0m4t10n_Runb00k_M1_Abus3}\n"
}

# ── Automation Account with system-assigned managed identity ──────────────────

resource "azurerm_automation_account" "automation_account" {
  name                = "aa-cmlnmbs-${random_integer.automation_account.result}"
  location            = azurerm_resource_group.automation_account.location
  resource_group_name = azurerm_resource_group.automation_account.name
  sku_name            = "Basic"

  identity {
    type = "SystemAssigned"
  }
}

# Grant the Automation Account's managed identity Storage Blob Data Reader
resource "azurerm_role_assignment" "aa_storage_reader" {
  scope                = azurerm_storage_account.flag.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = azurerm_automation_account.automation_account.identity[0].principal_id
}

# Legitimate runbook that the attacker will observe (and later replace / create new one)
resource "azurerm_automation_runbook" "hello" {
  name                    = "HelloWorld"
  location                = azurerm_resource_group.automation_account.location
  resource_group_name     = azurerm_resource_group.automation_account.name
  automation_account_name = azurerm_automation_account.automation_account.name
  log_verbose             = false
  log_progress            = false
  runbook_type            = "PowerShell"

  content = <<-PS
    Write-Output "Hello from Cumulonimbus Automation Account!"
    Write-Output "Run date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
  PS
}
