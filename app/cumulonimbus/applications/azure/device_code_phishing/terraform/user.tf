resource "random_password" "victim" {
  length           = 16
  special          = true
  override_special = "!@#"
  min_upper        = 2
  min_numeric      = 2
}

resource "azuread_user" "victim" {
  user_principal_name   = "dcp-victim${local.name_suffix_dash}@${var.tenant_domain}"
  display_name          = "DCP Victim${local.name_suffix_dash}"
  mail_nickname         = "dcp-victim${local.name_suffix_dash}"
  password              = random_password.victim.result
  force_password_change = false
}

# The victim has read access to the storage account containing the flag
resource "azurerm_role_assignment" "victim_blob_reader" {
  scope                = azurerm_storage_account.flag.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = azuread_user.victim.object_id
}
