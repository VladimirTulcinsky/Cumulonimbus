resource "random_integer" "blob_sas_abuse" {
  min = 1
  max = 999999
}

resource "azurerm_resource_group" "blob_sas_abuse" {
  name     = "blob-sas-abuse"
  location = "West Europe"
}

resource "azurerm_storage_account" "blob_sas_abuse" {
  name                     = "${var.app_name}sas${random_integer.blob_sas_abuse.result}"
  resource_group_name      = azurerm_resource_group.blob_sas_abuse.name
  location                 = azurerm_resource_group.blob_sas_abuse.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"

  # Static website to host the "web app" — intentionally public
  static_website {
    index_document     = "index.html"
    error_404_document = "404.html"
  }
}

# Overly-scoped SAS token: read+list across the entire storage account
# In a real scenario a developer hardcoded this to "simplify" client-side storage access
data "azurerm_storage_account_sas" "overpermissive" {
  connection_string = azurerm_storage_account.blob_sas_abuse.primary_connection_string
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

# Public web app — serves the index page and app.js
resource "azurerm_storage_blob" "index" {
  name                   = "index.html"
  storage_account_name   = azurerm_storage_account.blob_sas_abuse.name
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

# The vulnerability: SAS token hardcoded in client-side JavaScript
resource "azurerm_storage_blob" "app_js" {
  name                   = "app.js"
  storage_account_name   = azurerm_storage_account.blob_sas_abuse.name
  storage_container_name = "$web"
  type                   = "Block"
  content_type           = "application/javascript"
  source_content         = <<-EOF
    // Cumulonimbus Portal — storage client
    // TODO: move SAS token to backend before going to prod
    const STORAGE_ACCOUNT = "${azurerm_storage_account.blob_sas_abuse.name}";
    const SAS_TOKEN = "${data.azurerm_storage_account_sas.overpermissive.sas}";

    async function loadDocument(container, blob) {
      const url = `https://$${STORAGE_ACCOUNT}.blob.core.windows.net/$${container}/$${blob}$${SAS_TOKEN}`;
      const r = await fetch(url);
      return r.text();
    }
  EOF
}

# Private container — inaccessible without the SAS token
resource "azurerm_storage_container" "secrets" {
  name                  = "secrets"
  storage_account_name  = azurerm_storage_account.blob_sas_abuse.name
  container_access_type = "private"
}

resource "azurerm_storage_blob" "flag" {
  name                   = "flag.txt"
  storage_account_name   = azurerm_storage_account.blob_sas_abuse.name
  storage_container_name = azurerm_storage_container.secrets.name
  type                   = "Block"
  source_content         = "CUMULONIMBUS{SAS_T0k3n_N3v3r_1n_C0d3}\n"
}
