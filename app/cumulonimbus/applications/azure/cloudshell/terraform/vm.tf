resource "azurerm_resource_group" "vm_cs" {
  name     = "admin-vm-rg"
  location = "West Europe"
}

# Create virtual network
resource "azurerm_virtual_network" "vm_cs" {
  name                = "admin-vm-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.vm_cs.location
  resource_group_name = azurerm_resource_group.vm_cs.name
}

# Create subnet
resource "azurerm_subnet" "vm_cs" {
  name                 = "admin-vm-subnet"
  resource_group_name  = azurerm_resource_group.vm_cs.name
  virtual_network_name = azurerm_virtual_network.vm_cs.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Create public IPs
resource "azurerm_public_ip" "vm_cs" {
  name                = "admin-vm-public-ip"
  location            = azurerm_resource_group.vm_cs.location
  resource_group_name = azurerm_resource_group.vm_cs.name
  allocation_method   = "Dynamic"
}

# Create Network Security Group and rules
resource "azurerm_network_security_group" "vm_cs" {
  name                = "admin-vm-nsg"
  location            = azurerm_resource_group.vm_cs.location
  resource_group_name = azurerm_resource_group.vm_cs.name

  security_rule {
    name                       = "RDP"
    priority                   = 1000
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "3389"
    source_address_prefix      = "${var.attacker_public_ip}/32"
    destination_address_prefix = "*"
  }
}

# Create network interface
resource "azurerm_network_interface" "vm_cs" {
  name                = "admin-vm-nic"
  location            = azurerm_resource_group.vm_cs.location
  resource_group_name = azurerm_resource_group.vm_cs.name

  ip_configuration {
    name                          = "admin_vm_nic"
    subnet_id                     = azurerm_subnet.vm_cs.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.vm_cs.id
  }
}

# Connect the security group to the network interface
resource "azurerm_network_interface_security_group_association" "vm_cs" {
  network_interface_id      = azurerm_network_interface.vm_cs.id
  network_security_group_id = azurerm_network_security_group.vm_cs.id
}

# Create virtual machine
resource "azurerm_windows_virtual_machine" "vm_cs" {
  name                  = "admin-vm"
  admin_username        = "ytirucsboybytiruces"
  admin_password        = "IWillNotRememberThisPassword1."
  location              = azurerm_resource_group.vm_cs.location
  resource_group_name   = azurerm_resource_group.vm_cs.name
  network_interface_ids = [azurerm_network_interface.vm_cs.id]
  size                  = "Standard_B2s"

  os_disk {
    name                 = "adminVmDisk"
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "MicrosoftWindowsServer"
    offer     = "WindowsServer"
    sku       = "2022-datacenter-azure-edition"
    version   = "latest"
  }
}

resource "azurerm_virtual_machine_extension" "write_flag" {
  name                       = "write-flag"
  virtual_machine_id         = azurerm_windows_virtual_machine.vm_cs.id
  publisher                  = "Microsoft.Compute"
  type                       = "CustomScriptExtension"
  type_handler_version       = "1.8"
  auto_upgrade_minor_version = true

  settings = <<SETTINGS
    {
      "commandToExecute": "powershell.exe -Command \"New-Item 'C:/flag.txt' -ItemType File -Value 'Cumulonimbus{CSStorageMustBeLockedDown}'\""
    }
  SETTINGS
}


