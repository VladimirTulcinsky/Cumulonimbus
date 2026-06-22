terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.116"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.5.1"
    }
  }
}

# Authenticate with the service principal via environment variables:
#   ARM_CLIENT_ID, ARM_CLIENT_SECRET, ARM_TENANT_ID, ARM_SUBSCRIPTION_ID
# (the same service principal you use for the labs — it needs Contributor/Owner
# on the subscription to create the VM and its network).
provider "azurerm" {
  features {}
}

# Stable CTFd session signing key, generated once and persisted in state so it
# stays the same across VM reboots (sessions survive restarts).
resource "random_password" "ctfd_secret_key" {
  length  = 48
  special = false
}

# Singleton: fixed resource-group name (no random suffix). The first deployment
# claims it; any second `terraform apply` from a different state fails because
# azurerm_resource_group refuses to create a resource group that already exists.
# That guarantees only one shared CTFd can be stood up via this module.
resource "azurerm_resource_group" "ctfd" {
  name     = "cumulonimbus-ctfd"
  location = var.location
}

resource "azurerm_virtual_network" "ctfd" {
  name                = "ctfd-vnet"
  address_space       = ["10.50.0.0/16"]
  location            = azurerm_resource_group.ctfd.location
  resource_group_name = azurerm_resource_group.ctfd.name
}

resource "azurerm_subnet" "ctfd" {
  name                 = "ctfd-subnet"
  resource_group_name  = azurerm_resource_group.ctfd.name
  virtual_network_name = azurerm_virtual_network.ctfd.name
  address_prefixes     = ["10.50.1.0/24"]
}

resource "azurerm_public_ip" "ctfd" {
  name                = "ctfd-pip"
  location            = azurerm_resource_group.ctfd.location
  resource_group_name = azurerm_resource_group.ctfd.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_network_security_group" "ctfd" {
  name                = "ctfd-nsg"
  location            = azurerm_resource_group.ctfd.location
  resource_group_name = azurerm_resource_group.ctfd.name

  # SSH for admin troubleshooting. Restrict ssh_allowed_cidr to your IP.
  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = var.ssh_allowed_cidr
    destination_address_prefix = "*"
  }

  # The Azure CTFd scoreboard (container publishes 8001). Players reach this.
  security_rule {
    name                       = "CTFd-Azure"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8001"
    source_address_prefix      = var.player_allowed_cidr
    destination_address_prefix = "*"
  }
}

resource "azurerm_network_interface" "ctfd" {
  name                = "ctfd-nic"
  location            = azurerm_resource_group.ctfd.location
  resource_group_name = azurerm_resource_group.ctfd.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.ctfd.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.ctfd.id
  }
}

resource "azurerm_network_interface_security_group_association" "ctfd" {
  network_interface_id      = azurerm_network_interface.ctfd.id
  network_security_group_id = azurerm_network_security_group.ctfd.id
}

resource "azurerm_linux_virtual_machine" "ctfd" {
  name                = "ctfd-vm"
  resource_group_name = azurerm_resource_group.ctfd.name
  location            = azurerm_resource_group.ctfd.location
  size                = var.vm_size
  admin_username      = var.admin_username

  network_interface_ids = [azurerm_network_interface.ctfd.id]

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.admin_ssh_public_key
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "StandardSSD_LRS"
    disk_size_gb         = 64
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }

  # cloud-init: install Docker, clone the repo, and run the existing setup.py to
  # bring up + seed the shared Azure CTFd. Containers use restart=unless-stopped
  # and named volumes, so the scoreboard and its data survive reboots.
  custom_data = base64encode(templatefile("${path.module}/cloud-init.yaml", {
    repo_url       = var.repo_url
    git_ref        = var.git_ref
    admin_password = var.ctfd_admin_password
    secret_key     = random_password.ctfd_secret_key.result
  }))
}
