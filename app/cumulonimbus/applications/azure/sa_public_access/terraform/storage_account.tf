# Random id to avoid name collisions
resource "random_integer" "sa_public_access" {
  min = 1
  max = 999999
}

resource "azurerm_resource_group" "sa_public_access" {
  name     = "sa-public-access"
  location = "West Europe"
}

# Storage account to serve static content
resource "azurerm_storage_account" "sa_public_access" {
  name                     = "${var.app_name}${random_integer.sa_public_access.result}dev"
  resource_group_name      = azurerm_resource_group.sa_public_access.name
  location                 = azurerm_resource_group.sa_public_access.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"

  network_rules {
    default_action = "Deny"
    ip_rules       = [var.attacker_public_ip]
  }

  static_website {
    index_document     = "index.html"
    error_404_document = "404.html"
  }
}

# Add index.html and 404.html to the storage account
resource "azurerm_storage_blob" "index" {
  name                   = "index.html"
  storage_account_name   = azurerm_storage_account.sa_public_access.name
  storage_container_name = "$web"
  type                   = "Block"
  content_type           = "text/html"
  source_content         = <<EOF
<!DOCTYPE html>
<h1>Cumulonimbus Incorporation</h1>
<h2>WORK IN PROGRESS</h2>
<h3>There were some issues on the production environment, so we decided to remove it from the public for a while</h3>
EOF
}

resource "azurerm_storage_blob" "fourohfour" {
  name                   = "404.html"
  storage_account_name   = azurerm_storage_account.sa_public_access.name
  storage_container_name = "$web"
  type                   = "Block"
  content_type           = "text/html"
  source_content         = <<EOF
<!DOCTYPE html>
<h1>Cumulonimbus Incorporation</h1>
<h2>There's nothing here</h2>
EOF
}

# Storage account to scan with cloud-enum
resource "azurerm_storage_account" "sa_private_access" {
  name                     = "${var.app_name}${random_integer.sa_public_access.result}prd"
  resource_group_name      = azurerm_resource_group.sa_public_access.name
  location                 = azurerm_resource_group.sa_public_access.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"

  network_rules {
    default_action = "Deny"
    ip_rules       = [var.attacker_public_ip]
  }

  tags = {
    environment = "prd"
  }
}

# Container with container access
resource "azurerm_storage_container" "containeraccess" {
  name                  = "website"
  storage_account_name  = azurerm_storage_account.sa_private_access.name
  container_access_type = "container"
}

resource "azurerm_storage_blob" "server" {
  name                   = "server.js"
  storage_account_name   = azurerm_storage_account.sa_private_access.name
  storage_container_name = azurerm_storage_container.containeraccess.name
  type                   = "Block"
  source_content         = <<EOF
const express = require('express')
const app = express()
const port = 3000

app.get('/', (req, res) => {
  const fs = require('fs');

  // Read configuration file
  const config = JSON.parse(fs.readFileSync('config.cfg', 'utf8'));

  // Get BLOB from environment variable
  const blob = process.env.BLOB;

  // Append "flag.txt" to BLOB
  const blobWithFlag = blob + "flag.txt";

  // Only allow blob access and not container access
  console.log(blobWithFlag);
})

app.listen(port, () => {
  console.log(`Example app listening on port 3000`)
})

EOF
}

resource "azurerm_storage_blob" "hinttoflagblob" {
  name                   = "config.cfg"
  storage_account_name   = azurerm_storage_account.sa_private_access.name
  storage_container_name = azurerm_storage_container.containeraccess.name
  type                   = "Block"
  source_content         = <<EOF
NODE_ENV=development
BLOB=${azurerm_storage_container.flagcontainer.id}
PORT=3000

EOF
}

# Container with blob-level access
resource "azurerm_storage_container" "flagcontainer" {
  name                  = "secrets"
  storage_account_name  = azurerm_storage_account.sa_private_access.name
  container_access_type = "blob"
  
}

resource "azurerm_storage_blob" "flag" {
  name                   = "flag.txt"
  storage_account_name   = azurerm_storage_account.sa_private_access.name
  storage_container_name = azurerm_storage_container.flagcontainer.name
  type                   = "Block"
  source_content         = <<EOF
CUMULONIMBUS{St0r4g3_Acc0unt_4cc355}

EOF
}
