###############################################################################
# secrets_chain — one sequential lab that consolidates the "plaintext creds in
# an Azure resource" labs into a single attack path. Each stage's leaked value
# unlocks (or names) the next, ending at a Key Vault secret (the flag).
#
#   S1 public website  -> leaks a SAS token (in client-side JS)
#   S2 private blob     -> leaks the portal Service Principal's credentials
#   S3 SP login + RG tag-> names the App Configuration store
#   S4 App Configuration-> names the Data Factory
#   S5 Data Factory     -> linked-service connection string leaks a storage key
#   S6 storage blob     -> names the Container Instance
#   S7 Container Instance-> env vars leak the Key Vault + secret name
#   S8 Key Vault        -> the flag (SP already holds Secrets User)
#
# Genuine privilege boundaries: anonymous -> SAS -> service principal ->
# storage data-plane key -> Key Vault. The hops in between are discovery: the
# leaked plaintext value tells you where to look next.
###############################################################################

data "azuread_client_config" "current" {}
data "azurerm_client_config" "current" {}

resource "random_id" "suffix" {
  byte_length = 4
}

locals {
  suffix_alnum = lower(replace(var.name_suffix, "/[^a-zA-Z0-9]/", ""))
  base         = "${local.suffix_alnum}${random_id.suffix.hex}"

  rg_name      = "cumulonimbus-${var.app_id}-${random_id.suffix.hex}"
  sa_pub_name  = substr("cnchpub${local.base}", 0, 24)
  sa_data_name = substr("cnchdata${local.base}", 0, 24)
  appconf_name = substr("cnch-conf-${local.base}", 0, 50)
  adf_name     = substr("cnch-adf-${local.base}", 0, 63)
  aci_name     = "cnch-aci-${random_id.suffix.hex}"
  kv_name      = substr("cnchkv${local.base}", 0, 24)
  kv_secret    = "app-flag"
}

resource "azurerm_resource_group" "rg" {
  name     = local.rg_name
  location = var.location

  # S3 (discovery): a Reader can read resource-group tags. "For convenience"
  # someone recorded which App Configuration store holds the connection details.
  tags = {
    app_id         = var.app_id
    managed        = "terraform"
    "config-store" = local.appconf_name
    "ops-note"     = "service connection details centralised in app configuration"
  }

  depends_on = [
    azurerm_resource_provider_registration.microsoft_appconfiguration,
    azurerm_resource_provider_registration.microsoft_datafactory,
    azurerm_resource_provider_registration.microsoft_containerinstance,
  ]
}

# ── Portal service principal (the attacker's identity, leaked in S2) ──────────
resource "azuread_application" "portal" {
  display_name = "cumulonimbus-portal-${random_id.suffix.hex}"
}

resource "azuread_service_principal" "portal" {
  client_id = azuread_application.portal.client_id
}

resource "azuread_application_password" "portal" {
  application_id = azuread_application.portal.id
  display_name   = "portal-client-secret"
  end_date       = "2030-01-01T00:00:00Z"
}

# The SP's access: Reader on the RG (control-plane reads for S3/S5/S7), App
# Configuration Data Reader (S4), and Key Vault Secrets User (S8 payoff).
resource "azurerm_role_assignment" "portal_reader" {
  scope                = azurerm_resource_group.rg.id
  role_definition_name = "Reader"
  principal_id         = azuread_service_principal.portal.object_id
}

###############################################################################
# S1 — Public static website leaking an over-scoped SAS token
###############################################################################
resource "azurerm_storage_account" "pub" {
  name                     = local.sa_pub_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"

  static_website {
    index_document     = "index.html"
    error_404_document = "404.html"
  }

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# Over-scoped SAS: read+list across the whole account (a developer's shortcut).
data "azurerm_storage_account_sas" "pub" {
  connection_string = azurerm_storage_account.pub.primary_connection_string
  https_only        = true
  signed_version    = "2019-12-12"

  resource_types {
    service   = true
    container = true
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
    list    = true
    add     = false
    create  = false
    update  = false
    process = false
    tag     = false
    filter  = false
  }
}

resource "azurerm_storage_blob" "index" {
  name                   = "index.html"
  storage_account_name   = azurerm_storage_account.pub.name
  storage_container_name = "$web"
  type                   = "Block"
  content_type           = "text/html"
  source_content         = <<-EOF
    <!DOCTYPE html>
    <html>
    <head><title>Cumulonimbus Portal</title></head>
    <body>
      <h1>Cumulonimbus Employee Portal</h1>
      <p>Internal portal — authorised users only.</p>
      <script src="app.js"></script>
    </body>
    </html>
  EOF
}

# The vulnerability: SAS token hardcoded in client-side JavaScript.
resource "azurerm_storage_blob" "app_js" {
  name                   = "app.js"
  storage_account_name   = azurerm_storage_account.pub.name
  storage_container_name = "$web"
  type                   = "Block"
  content_type           = "application/javascript"
  source_content         = <<-EOF
    // Cumulonimbus Portal - storage client
    // TODO: move SAS token to backend before going to prod
    const STORAGE_ACCOUNT = "${azurerm_storage_account.pub.name}";
    const SAS_TOKEN = "${data.azurerm_storage_account_sas.pub.sas}";

    async function loadDocument(container, blob) {
      const url = `https://$${STORAGE_ACCOUNT}.blob.core.windows.net/$${container}/$${blob}$${SAS_TOKEN}`;
      const r = await fetch(url);
      return r.text();
    }
  EOF
}

###############################################################################
# S2 — Private blob (reachable with the SAS) leaking the SP credentials
###############################################################################
resource "azurerm_storage_container" "onboarding" {
  name                  = "onboarding"
  storage_account_name  = azurerm_storage_account.pub.name
  container_access_type = "private"
}

resource "azurerm_storage_blob" "onboarding" {
  name                   = "onboarding.txt"
  storage_account_name   = azurerm_storage_account.pub.name
  storage_container_name = azurerm_storage_container.onboarding.name
  type                   = "Block"
  source_content         = <<-EOF
    Welcome to the platform team.

    Portal automation service principal (used by the deploy pipeline):
      AZURE_CLIENT_ID=${azuread_service_principal.portal.client_id}
      AZURE_CLIENT_SECRET=${azuread_application_password.portal.value}
      AZURE_TENANT_ID=${data.azuread_client_config.current.tenant_id}

    Sign in with:
      az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID
  EOF
}

###############################################################################
# S4 — App Configuration (SP has Data Reader) naming the Data Factory
###############################################################################
resource "azurerm_app_configuration" "conf" {
  name                = local.appconf_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  # "standard" (not "free"): the free tier allows only one store per
  # subscription, which would collide in a shared/multi-player CTF.
  sku = "standard"

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "azurerm_role_assignment" "portal_appconf_reader" {
  scope                = azurerm_app_configuration.conf.id
  role_definition_name = "App Configuration Data Reader"
  principal_id         = azuread_service_principal.portal.object_id
}

# Decoys + the real pointer to the next stage.
resource "azurerm_app_configuration_key" "env" {
  configuration_store_id = azurerm_app_configuration.conf.id
  key                    = "app/environment"
  value                  = "production"
  depends_on             = [azurerm_role_assignment.portal_appconf_reader]
}

resource "azurerm_app_configuration_key" "db_host" {
  configuration_store_id = azurerm_app_configuration.conf.id
  key                    = "database/host"
  value                  = "prod-db.internal.example.com"
  depends_on             = [azurerm_role_assignment.portal_appconf_reader]
}

resource "azurerm_app_configuration_key" "adf_pointer" {
  configuration_store_id = azurerm_app_configuration.conf.id
  key                    = "pipeline/data-factory-name"
  value                  = local.adf_name
  depends_on             = [azurerm_role_assignment.portal_appconf_reader]
}

resource "azurerm_app_configuration_key" "adf_note" {
  configuration_store_id = azurerm_app_configuration.conf.id
  key                    = "pipeline/note"
  value                  = "Data Factory linked services hold the storage connection strings."
  depends_on             = [azurerm_role_assignment.portal_appconf_reader]
}

###############################################################################
# S5 — Data Factory linked service leaking a REAL storage account key
###############################################################################
resource "azurerm_storage_account" "data" {
  name                     = local.sa_data_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "azurerm_data_factory" "adf" {
  name                = local.adf_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# The connection string embeds the live primary key of the "data" account, so
# the leaked credential genuinely unlocks the next stage's blob.
resource "azurerm_data_factory_linked_service_azure_blob_storage" "data" {
  name              = "DataLakeConnection"
  data_factory_id   = azurerm_data_factory.adf.id
  description       = "Primary data lake storage connection"
  connection_string = "DefaultEndpointsProtocol=https;AccountName=${azurerm_storage_account.data.name};AccountKey=${azurerm_storage_account.data.primary_access_key};EndpointSuffix=core.windows.net"
}

###############################################################################
# S6 — Private blob (reachable with the leaked storage key) naming the ACI
###############################################################################
resource "azurerm_storage_container" "runtime" {
  name                  = "runtime"
  storage_account_name  = azurerm_storage_account.data.name
  container_access_type = "private"
}

resource "azurerm_storage_blob" "runtime" {
  name                   = "runtime.json"
  storage_account_name   = azurerm_storage_account.data.name
  storage_container_name = azurerm_storage_container.runtime.name
  type                   = "Block"
  content_type           = "application/json"
  source_content = jsonencode({
    service         = "cumulonimbus-portal"
    container_group = local.aci_name
    note            = "Runtime container loads its secrets coordinates from environment variables."
  })
}

###############################################################################
# S7 — Container Instance whose env vars leak the Key Vault + secret name
###############################################################################
resource "azurerm_container_group" "app" {
  name                = local.aci_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  ip_address_type     = "None"
  os_type             = "Linux"
  restart_policy      = "Never"

  container {
    name   = "app"
    image  = "alpine:3.18"
    cpu    = "0.5"
    memory = "0.5"

    commands = ["sh", "-c", "echo Starting application && sleep 3600"]

    environment_variables = {
      "APP_ENV"          = "production"
      "KEY_VAULT_NAME"   = local.kv_name
      "KEY_VAULT_SECRET" = local.kv_secret
      "NOTE"             = "secret retrieved at startup from Key Vault"
    }

    secure_environment_variables = {}

    ports {
      port     = 8080
      protocol = "TCP"
    }
  }

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}
