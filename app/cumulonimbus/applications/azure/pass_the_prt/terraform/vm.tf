resource "azurerm_resource_group" "ptp" {
  name     = "pass-the-prt-${random_id.suffix.hex}"
  location = "northeurope"
}

resource "time_sleep" "rg_propagation" {
  depends_on      = [azurerm_resource_group.ptp]
  create_duration = "15s"
}

resource "azurerm_virtual_network" "ptp" {
  depends_on          = [time_sleep.rg_propagation]
  name                = "vnet-ptp-${random_id.suffix.hex}"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.ptp.location
  resource_group_name = azurerm_resource_group.ptp.name
}

resource "azurerm_subnet" "ptp" {
  name                 = "subnet-ptp"
  resource_group_name  = azurerm_resource_group.ptp.name
  virtual_network_name = azurerm_virtual_network.ptp.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_public_ip" "ptp" {
  name                = "pip-ptp-${random_id.suffix.hex}"
  location            = azurerm_resource_group.ptp.location
  resource_group_name = azurerm_resource_group.ptp.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_network_security_group" "ptp" {
  name                = "nsg-ptp-${random_id.suffix.hex}"
  location            = azurerm_resource_group.ptp.location
  resource_group_name = azurerm_resource_group.ptp.name

  security_rule {
    name                       = "allow-rdp"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "3389"
    source_address_prefix      = local.attacker_public_ip_cidr
    destination_address_prefix = "*"
  }
}

resource "azurerm_network_interface" "ptp" {
  name                = "nic-ptp-${random_id.suffix.hex}"
  location            = azurerm_resource_group.ptp.location
  resource_group_name = azurerm_resource_group.ptp.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.ptp.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.ptp.id
  }
}

resource "azurerm_network_interface_security_group_association" "ptp" {
  network_interface_id      = azurerm_network_interface.ptp.id
  network_security_group_id = azurerm_network_security_group.ptp.id
}

resource "azurerm_windows_virtual_machine" "ptp" {
  name                  = "vm-ptp-${random_id.suffix.hex}"
  resource_group_name   = azurerm_resource_group.ptp.name
  location              = azurerm_resource_group.ptp.location
  size                  = "Standard_D2s_v3"
  admin_username        = "attacker"
  admin_password        = random_password.attacker.result
  network_interface_ids = [azurerm_network_interface.ptp.id]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "MicrosoftWindowsServer"
    offer     = "WindowsServer"
    sku       = "2022-datacenter-azure-edition"
    version   = "latest"
  }

  # The AADLoginForWindows v2 (Secure VM Join) uses the managed identity to
  # authenticate to Azure AD during device registration.
  identity {
    type = "SystemAssigned"
  }
}

# Join the VM to Azure AD so Azure AD users can sign in interactively.
# The AADLoginForWindows extension also provisions the CloudAP plugin that
# issues PRTs when Azure AD users authenticate to this device.
resource "azurerm_virtual_machine_extension" "aad_login" {
  name                       = "AADLoginForWindows"
  virtual_machine_id         = azurerm_windows_virtual_machine.ptp.id
  publisher                  = "Microsoft.Azure.ActiveDirectory"
  type                       = "AADLoginForWindows"
  type_handler_version       = "2.0"
  auto_upgrade_minor_version = true
  settings = jsonencode({ mdmId = "", tenantId = var.tenant_id })
}

# Disable Defender, install Mimikatz, turn off Windows Firewall.
# Uses -EncodedCommand (UTF-16LE base64) to avoid cmd.exe quote stripping.
resource "azurerm_virtual_machine_extension" "setup" {
  name                       = "setup"
  virtual_machine_id         = azurerm_windows_virtual_machine.ptp.id
  publisher                  = "Microsoft.Compute"
  type                       = "CustomScriptExtension"
  type_handler_version       = "1.10"
  auto_upgrade_minor_version = true

  settings = jsonencode({
    commandToExecute = "powershell.exe -NoProfile -NonInteractive -EncodedCommand UwBlAHQALQBNAHAAUAByAGUAZgBlAHIAZQBuAGMAZQAgAC0ARABpAHMAYQBiAGwAZQBSAGUAYQBsAHQAaQBtAGUATQBvAG4AaQB0AG8AcgBpAG4AZwAgACQAdAByAHUAZQAgAC0ARgBvAHIAYwBlAAoAQQBkAGQALQBNAHAAUAByAGUAZgBlAHIAZQBuAGMAZQAgAC0ARQB4AGMAbAB1AHMAaQBvAG4AUABhAHQAaAAgACcAQwA6AFwAVABvAG8AbABzACcACgBOAGUAdwAtAEkAdABlAG0AIAAtAEkAdABlAG0AVAB5AHAAZQAgAEQAaQByAGUAYwB0AG8AcgB5ACAALQBQAGEAdABoACAAJwBDADoAXABUAG8AbwBsAHMAJwAgAC0ARgBvAHIAYwBlAAoAWwBOAGUAdAAuAFMAZQByAHYAaQBjAGUAUABvAGkAbgB0AE0AYQBuAGEAZwBlAHIAXQA6ADoAUwBlAGMAdQByAGkAdAB5AFAAcgBvAHQAbwBjAG8AbAAgAD0AIABbAE4AZQB0AC4AUwBlAGMAdQByAGkAdAB5AFAAcgBvAHQAbwBjAG8AbABUAHkAcABlAF0AOgA6AFQAbABzADEAMgAKAEkAbgB2AG8AawBlAC0AVwBlAGIAUgBlAHEAdQBlAHMAdAAgAC0AVQByAGkAIAAnAGgAdAB0AHAAcwA6AC8ALwBnAGkAdABoAHUAYgAuAGMAbwBtAC8AZwBlAG4AdABpAGwAawBpAHcAaQAvAG0AaQBtAGkAawBhAHQAegAvAHIAZQBsAGUAYQBzAGUAcwAvAGQAbwB3AG4AbABvAGEAZAAvADIALgAyAC4AMAAtADIAMAAyADIAMAA5ADEAOQAvAG0AaQBtAGkAawBhAHQAegBfAHQAcgB1AG4AawAuAHoAaQBwACcAIAAtAE8AdQB0AEYAaQBsAGUAIAAnAEMAOgBcAFQAbwBvAGwAcwBcAG0AaQBtAGkAawBhAHQAegAuAHoAaQBwACcAIAAtAFUAcwBlAEIAYQBzAGkAYwBQAGEAcgBzAGkAbgBnAAoARQB4AHAAYQBuAGQALQBBAHIAYwBoAGkAdgBlACAALQBQAGEAdABoACAAJwBDADoAXABUAG8AbwBsAHMAXABtAGkAbQBpAGsAYQB0AHoALgB6AGkAcAAnACAALQBEAGUAcwB0AGkAbgBhAHQAaQBvAG4AUABhAHQAaAAgACcAQwA6AFwAVABvAG8AbABzAFwAbQBpAG0AaQBrAGEAdAB6ACcAIAAtAEYAbwByAGMAZQAKAFMAZQB0AC0ASQB0AGUAbQBQAHIAbwBwAGUAcgB0AHkAIAAtAFAAYQB0AGgAIAAnAEgASwBMAE0AOgBcAFMATwBGAFQAVwBBAFIARQBcAE0AaQBjAHIAbwBzAG8AZgB0AFwAQQBjAHQAaQB2AGUAIABTAGUAdAB1AHAAXABJAG4AcwB0AGEAbABsAGUAZAAgAEMAbwBtAHAAbwBuAGUAbgB0AHMAXAB7AEEANQAwADkAQgAxAEEANwAtADMANwBFAEYALQA0AGIAMwBmAC0AOABDAEYAQwAtADQARgAzAEEANwA0ADcAMAA0ADAANwAzAH0AJwAgAC0ATgBhAG0AZQAgAEkAcwBJAG4AcwB0AGEAbABsAGUAZAAgAC0AVgBhAGwAdQBlACAAMAAKAG4AZQB0AHMAaAAgAGEAZAB2AGYAaQByAGUAdwBhAGwAbAAgAHMAZQB0ACAAYQBsAGwAcAByAG8AZgBpAGwAZQBzACAAcwB0AGEAdABlACAAbwBmAGYACgBTAGUAdAAtAFQAaQBtAGUAWgBvAG4AZQAgAC0ASQBkACAAJwBXAC4AIABFAHUAcgBvAHAAZQAgAFMAdABhAG4AZABhAHIAZAAgAFQAaQBtAGUAJwAKAFMAZQB0AC0ASQB0AGUAbQBQAHIAbwBwAGUAcgB0AHkAIAAtAFAAYQB0AGgAIAAnAEgASwBMAE0AOgBcAFMAWQBTAFQARQBNAFwAQwB1AHIAcgBlAG4AdABDAG8AbgB0AHIAbwBsAFMAZQB0AFwAUwBlAHIAdgBpAGMAZQBzAFwAVwAzADIAVABpAG0AZQBcAFQAaQBtAGUAUAByAG8AdgBpAGQAZQByAHMAXABWAE0ASQBDAFQAaQBtAGUAUAByAG8AdgBpAGQAZQByACcAIAAtAE4AYQBtAGUAIABFAG4AYQBiAGwAZQBkACAALQBWAGEAbAB1AGUAIAAwAAoAdwAzADIAdABtACAALwByAGUAZwBpAHMAdABlAHIACgBTAGUAdAAtAFMAZQByAHYAaQBjAGUAIAAtAE4AYQBtAGUAIABXADMAMgBUAGkAbQBlACAALQBTAHQAYQByAHQAdQBwAFQAeQBwAGUAIABBAHUAdABvAG0AYQB0AGkAYwAgAC0ARQByAHIAbwByAEEAYwB0AGkAbwBuACAAUwBpAGwAZQBuAHQAbAB5AEMAbwBuAHQAaQBuAHUAZQAKAFMAdABhAHIAdAAtAFMAZQByAHYAaQBjAGUAIABXADMAMgBUAGkAbQBlACAALQBFAHIAcgBvAHIAQQBjAHQAaQBvAG4AIABTAGkAbABlAG4AdABsAHkAQwBvAG4AdABpAG4AdQBlAAoAdwAzADIAdABtACAALwBjAG8AbgBmAGkAZwAgAC8AbQBhAG4AdQBhAGwAcABlAGUAcgBsAGkAcwB0ADoAJwB0AGkAbQBlAC4AdwBpAG4AZABvAHcAcwAuAGMAbwBtACcAIAAvAHMAeQBuAGMAZgByAG8AbQBmAGwAYQBnAHMAOgBtAGEAbgB1AGEAbAAgAC8AcgBlAGwAaQBhAGIAbABlADoAWQBFAFMAIAAvAHUAcABkAGEAdABlAAoAdwAzADIAdABtACAALwByAGUAcwB5AG4AYwAgAC8AZgBvAHIAYwBlAA=="
  })

  depends_on = [azurerm_virtual_machine_extension.aad_login]
}

# Configure autologon for the victim user so their PRT is seeded into LSASS
# automatically on first boot — no interactive login required from the player.
# azurerm_virtual_machine_run_command supports multi-line scripts and Terraform
# interpolations cleanly, unlike CSE which requires UTF-16LE base64 encoding.
resource "azurerm_virtual_machine_run_command" "seed_prt" {
  name               = "seed-prt"
  location           = azurerm_resource_group.ptp.location
  virtual_machine_id = azurerm_windows_virtual_machine.ptp.id

  source {
    script = <<-PS
      $r = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon'
      Set-ItemProperty $r -Name AutoAdminLogon    -Value '1'
      Set-ItemProperty $r -Name DefaultUserName   -Value 'AzureAD\${azuread_user.victim.user_principal_name}'
      Set-ItemProperty $r -Name DefaultDomainName -Value ''
      Set-ItemProperty $r -Name DefaultPassword   -Value '${random_password.victim.result}'
      Set-ItemProperty $r -Name AutoLogonCount    -Value '1'
      $a = New-ScheduledTaskAction -Execute 'shutdown.exe' -Argument '/r /t 60 /f'
      $t = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddMinutes(2))
      $p = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -RunLevel Highest
      Register-ScheduledTask -Force -TaskName 'PrtSeed' -Action $a -Trigger $t -Principal $p
      Start-ScheduledTask -TaskName 'PrtSeed'
    PS
  }

  depends_on = [azurerm_virtual_machine_extension.setup]
}

# Cost control: auto-deallocate this VM daily (Azure stops compute billing
# when a VM is deallocated). Change daily_recurrence_time/timezone to suit;
# restart the VM from the portal or `az vm start` when you need it again.
resource "azurerm_dev_test_global_vm_shutdown_schedule" "ptp" {
  virtual_machine_id    = azurerm_windows_virtual_machine.ptp.id
  location              = azurerm_windows_virtual_machine.ptp.location
  enabled               = true
  daily_recurrence_time = "1900"
  timezone              = "UTC"

  notification_settings {
    enabled = false
  }
}
