# Simulates an initiative that an administrator deployed for compliance monitoring.
# The managed identity was lazily granted Owner instead of the specific roles needed.

resource "azurerm_policy_definition" "audit_storage_tag" {
  name         = "audit-storage-tag-${random_id.suffix.hex}"
  policy_type  = "Custom"
  mode         = "All"
  display_name = "Audit storage accounts for monitoring tag"
  description  = "Audits storage accounts that are missing the 'monitoring' tag."

  policy_rule = jsonencode({
    if = {
      allOf = [
        { field = "type", equals = "Microsoft.Storage/storageAccounts" },
        { field = "tags['monitoring']", exists = "false" }
      ]
    }
    then = {
      effect = "Audit"
    }
  })
}

resource "azurerm_policy_set_definition" "monitoring_initiative" {
  name         = "monitoring-initiative-${random_id.suffix.hex}"
  policy_type  = "Custom"
  display_name = "Monitoring Compliance Initiative"
  description  = "Ensures all resources meet monitoring requirements."

  policy_definition_reference {
    policy_definition_id = azurerm_policy_definition.audit_storage_tag.id
    reference_id         = "audit_storage_tag"
  }
}

resource "azurerm_subscription_policy_assignment" "monitoring_assignment" {
  name                 = "monitoring-${random_id.suffix.hex}"
  subscription_id      = "/subscriptions/${var.subscription_id}"
  policy_definition_id = azurerm_policy_set_definition.monitoring_initiative.id
  display_name         = "Monitoring Compliance Assignment"
  location             = "westeurope"

  # System-assigned identity — needed when DeployIfNotExists policies are in the initiative.
  # Misconfiguration: the administrator granted this identity Owner on the subscription
  # instead of the minimum required roles.
  identity {
    type = "SystemAssigned"
  }
}

# The misconfiguration: Owner granted to the managed identity for "convenience"
resource "azurerm_role_assignment" "managed_identity_owner" {
  scope                = "/subscriptions/${var.subscription_id}"
  role_definition_name = "Owner"
  principal_id         = azurerm_subscription_policy_assignment.monitoring_assignment.identity[0].principal_id
}

# Allow RBAC to propagate before resources that depend on role assignments
resource "time_sleep" "rbac_propagation" {
  depends_on      = [azurerm_role_assignment.managed_identity_owner]
  create_duration = "30s"
}
