resource "random_id" "suffix" {
  byte_length = 4
}

locals {
  rg_name  = "cumulonimbus-${var.app_id}-${random_id.suffix.hex}"
  vm_name  = "cnimbus-vm-${random_id.suffix.hex}"
  location = "West Europe"
}

resource "azurerm_resource_group" "rg" {
  name     = local.rg_name
  location = local.location
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "azurerm_virtual_network" "vnet" {
  name                = "cnimbus-vnet-${random_id.suffix.hex}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = local.location
  address_space       = ["10.0.0.0/16"]
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "azurerm_subnet" "subnet" {
  name                 = "default"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_network_interface" "nic" {
  name                = "cnimbus-nic-${random_id.suffix.hex}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = local.location

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "azurerm_linux_virtual_machine" "vm" {
  name                            = local.vm_name
  resource_group_name             = azurerm_resource_group.rg.name
  location                        = local.location
  size                            = "Standard_D2s_v3"
  admin_username                  = "azureuser"
  disable_password_authentication = true

  network_interface_ids = [azurerm_network_interface.nic.id]

  admin_ssh_key {
    username   = "azureuser"
    public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC0placeholder+cumulonimbus/placeholder== placeholder@cumulonimbus"
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

  # Write the flag to a file during first boot
  custom_data = base64encode(<<-CLOUD_INIT
    #!/bin/bash
    echo 'CUMULONIMBUS{VM_RunC0mm4nd_Arb1tr4ry_Exec}' > /root/flag.txt
    chmod 600 /root/flag.txt
  CLOUD_INIT
  )

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# Attacker user with Virtual Machine Contributor — includes Microsoft.Compute/virtualMachines/runCommand/action
data "azuread_client_config" "current" {}

resource "azuread_user" "attacker" {
  user_principal_name   = "attacker-${random_id.suffix.hex}@${data.azuread_client_config.current.tenant_id}.onmicrosoft.com"
  display_name          = "Cumulonimbus Attacker ${random_id.suffix.hex}"
  password              = "C@ttack3r!${random_id.suffix.hex}"
  force_password_change = false
}

resource "azurerm_role_assignment" "attacker_vm_contributor" {
  scope                = azurerm_resource_group.rg.id
  role_definition_name = "Virtual Machine Contributor"
  principal_id         = azuread_user.attacker.object_id
}
