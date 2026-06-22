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

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# Custom Script Extension — the settings block is NOT encrypted and is readable
# via ARM by any Reader. The commandToExecute contains the flag.
resource "azurerm_virtual_machine_extension" "script" {
  name                 = "configure-app"
  virtual_machine_id   = azurerm_linux_virtual_machine.vm.id
  publisher            = "Microsoft.Azure.Extensions"
  type                 = "CustomScript"
  type_handler_version = "2.1"

  # settings is plaintext in ARM — readable by any Reader via az vm extension show
  settings = jsonencode({
    commandToExecute = "echo 'CUMULONIMBUS{VM_3xt3ns10n_S3tt1ngs_Pl41nt3xt}' > /tmp/app.conf && chmod 600 /tmp/app.conf"
  })

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# Attacker user with Reader on the resource group
data "azuread_client_config" "current" {}

resource "azuread_user" "attacker" {
  user_principal_name   = "attacker-${random_id.suffix.hex}@${var.tenant_domain}"
  display_name          = "Cumulonimbus Attacker ${random_id.suffix.hex}"
  password              = "C@ttack3r!${random_id.suffix.hex}"
  force_password_change = false
}

resource "azurerm_role_assignment" "attacker_reader" {
  scope                = azurerm_resource_group.rg.id
  role_definition_name = "Reader"
  principal_id         = azuread_user.attacker.object_id
}

# Cost control: auto-deallocate this VM daily (Azure stops compute billing
# when a VM is deallocated). Change daily_recurrence_time/timezone to suit;
# restart the VM from the portal or `az vm start` when you need it again.
resource "azurerm_dev_test_global_vm_shutdown_schedule" "vm" {
  virtual_machine_id    = azurerm_linux_virtual_machine.vm.id
  location              = azurerm_linux_virtual_machine.vm.location
  enabled               = true
  daily_recurrence_time = "1900"
  timezone              = "UTC"

  notification_settings {
    enabled = false
  }
}
