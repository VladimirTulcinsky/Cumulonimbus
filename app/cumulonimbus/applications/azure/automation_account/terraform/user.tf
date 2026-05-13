data "azuread_domains" "automation_account" {
  only_initial = true
}

resource "random_password" "attacker" {
  length           = 16
  special          = true
  override_special = "!@#"
  min_upper        = 2
  min_numeric      = 2
}

resource "azuread_user" "attacker" {
  user_principal_name   = "aa-attacker@${data.azuread_domains.automation_account.domains[0].domain_name}"
  display_name          = "AA Attacker"
  mail_nickname         = "aa-attacker"
  password              = random_password.attacker.result
  force_password_change = false
}

# Misconfiguration: Automation Contributor lets a user create and run runbooks,
# which execute as the Automation Account's managed identity.
resource "azurerm_role_assignment" "attacker_automation_contributor" {
  scope                = azurerm_automation_account.automation_account.id
  role_definition_name = "Automation Contributor"
  principal_id         = azuread_user.attacker.object_id
}
