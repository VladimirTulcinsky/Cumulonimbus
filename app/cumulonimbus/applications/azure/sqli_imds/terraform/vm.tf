resource "azurerm_resource_group" "sqli_imds" {
  name     = "sqli-imds-${random_id.suffix.hex}"
  location = "westeurope"
}

resource "time_sleep" "rg_propagation" {
  depends_on      = [azurerm_resource_group.sqli_imds]
  create_duration = "15s"
}

resource "azurerm_virtual_network" "sqli_imds" {
  depends_on          = [time_sleep.rg_propagation]
  name                = "vnet-sqli-imds-${random_id.suffix.hex}"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.sqli_imds.location
  resource_group_name = azurerm_resource_group.sqli_imds.name
}

resource "azurerm_subnet" "sqli_imds" {
  name                 = "subnet-sqli-imds"
  resource_group_name  = azurerm_resource_group.sqli_imds.name
  virtual_network_name = azurerm_virtual_network.sqli_imds.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_public_ip" "sqli_imds" {
  name                = "pip-sqli-imds-${random_id.suffix.hex}"
  location            = azurerm_resource_group.sqli_imds.location
  resource_group_name = azurerm_resource_group.sqli_imds.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_network_security_group" "sqli_imds" {
  name                = "nsg-sqli-imds-${random_id.suffix.hex}"
  location            = azurerm_resource_group.sqli_imds.location
  resource_group_name = azurerm_resource_group.sqli_imds.name

  security_rule {
    name                       = "allow-http"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = local.attacker_public_ip_cidr
    destination_address_prefix = "*"
  }
}

resource "azurerm_network_interface" "sqli_imds" {
  name                = "nic-sqli-imds-${random_id.suffix.hex}"
  location            = azurerm_resource_group.sqli_imds.location
  resource_group_name = azurerm_resource_group.sqli_imds.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.sqli_imds.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.sqli_imds.id
  }
}

resource "azurerm_network_interface_security_group_association" "sqli_imds" {
  network_interface_id      = azurerm_network_interface.sqli_imds.id
  network_security_group_id = azurerm_network_security_group.sqli_imds.id
}

resource "azurerm_linux_virtual_machine" "sqli_imds" {
  name                            = "vm-sqli-imds-${random_id.suffix.hex}"
  resource_group_name             = azurerm_resource_group.sqli_imds.name
  location                        = azurerm_resource_group.sqli_imds.location
  size                            = "Standard_D2s_v3"
  admin_username                  = "azureuser"
  disable_password_authentication = true

  network_interface_ids = [azurerm_network_interface.sqli_imds.id]

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
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_virtual_machine_extension" "setup" {
  name                 = "setup"
  virtual_machine_id   = azurerm_linux_virtual_machine.sqli_imds.id
  publisher            = "Microsoft.Azure.Extensions"
  type                 = "CustomScript"
  type_handler_version = "2.1"

  settings = jsonencode({
    script = base64encode(file("${path.module}/../files/setup.sh"))
  })
}

# Cost control: auto-deallocate this VM daily (Azure stops compute billing
# when a VM is deallocated). Change daily_recurrence_time/timezone to suit;
# restart the VM from the portal or `az vm start` when you need it again.
resource "azurerm_dev_test_global_vm_shutdown_schedule" "sqli_imds" {
  virtual_machine_id    = azurerm_linux_virtual_machine.sqli_imds.id
  location              = azurerm_linux_virtual_machine.sqli_imds.location
  enabled               = true
  daily_recurrence_time = "1900"
  timezone              = "UTC"

  notification_settings {
    enabled = false
  }
}
