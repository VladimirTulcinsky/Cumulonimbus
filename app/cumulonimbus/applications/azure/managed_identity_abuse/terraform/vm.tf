resource "random_integer" "managed_identity_abuse" {
  min = 1
  max = 999999
}

resource "azurerm_resource_group" "managed_identity_abuse" {
  name     = "managed-identity-abuse"
  location = var.location
}

resource "azurerm_virtual_network" "managed_identity_abuse" {
  name                = "vnet-mia-${random_integer.managed_identity_abuse.result}"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.managed_identity_abuse.location
  resource_group_name = azurerm_resource_group.managed_identity_abuse.name
}

resource "azurerm_subnet" "managed_identity_abuse" {
  name                 = "subnet-mia"
  resource_group_name  = azurerm_resource_group.managed_identity_abuse.name
  virtual_network_name = azurerm_virtual_network.managed_identity_abuse.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_network_interface" "managed_identity_abuse" {
  name                = "nic-mia-${random_integer.managed_identity_abuse.result}"
  location            = azurerm_resource_group.managed_identity_abuse.location
  resource_group_name = azurerm_resource_group.managed_identity_abuse.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.managed_identity_abuse.id
    private_ip_address_allocation = "Dynamic"
  }
}

# The victim VM — system-assigned managed identity is over-privileged
resource "azurerm_linux_virtual_machine" "managed_identity_abuse" {
  name                            = "vm-mia-${random_integer.managed_identity_abuse.result}"
  resource_group_name             = azurerm_resource_group.managed_identity_abuse.name
  location                        = azurerm_resource_group.managed_identity_abuse.location
  size                            = "Standard_D2s_v3"
  admin_username                  = "azureuser"
  disable_password_authentication = true

  network_interface_ids = [azurerm_network_interface.managed_identity_abuse.id]

  admin_ssh_key {
    username   = "azureuser"
    public_key = file("./../../../../.data/.ssh/${var.app_id}.pub")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  # The misconfiguration: system-assigned identity with Storage Blob Data Reader
  identity {
    type = "SystemAssigned"
  }
}

# Grant the managed identity Storage Blob Data Reader on the flag storage account
resource "azurerm_role_assignment" "mi_storage_reader" {
  scope                = azurerm_storage_account.flag_storage.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = azurerm_linux_virtual_machine.managed_identity_abuse.identity[0].principal_id
}
