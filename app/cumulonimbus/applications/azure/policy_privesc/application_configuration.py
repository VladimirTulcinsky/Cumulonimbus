from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):

    def get_flag(self) -> str:
        return "CUMULONIMBUS{PolicyPrivEsc_DeployIfNotExists_OwnerRole}"

    def get_difficulty(self) -> str:
        return "Advanced"

    def get_hints(self) -> dict:
        return {
            1: "You have Resource Policy Contributor on the subscription. Enumerate existing policy assignments and check what roles their managed identities hold: `az policy assignment list` + `az role assignment list --all`.",
            2: "The monitoring initiative's managed identity has Owner on the subscription. Resource Policy Contributor lets you update initiative definitions — you can inject an additional policy without touching the existing assignment.",
            3: "Create a DeployIfNotExists policy whose ARM template deploys a Microsoft.Authorization/roleAssignment granting you Owner on the remediation scope. Add it to the initiative, then run: `az policy remediation create --policy-assignment <id> --definition-reference-id <ref> --resource-group <target-rg>`.",
        }

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("\n=== Azure Policy Privilege Escalation Lab ===")
        print(f"  Attacker UPN            : {output.get('policyuser_upn', {}).get('value', 'N/A')}")
        print(f"  Attacker password       : {output.get('policyuser_password', {}).get('value', 'N/A')}")
        print(f"  Subscription ID         : {output.get('subscription_id', {}).get('value', 'N/A')}")
        print(f"  Target resource group   : {output.get('target_resource_group', {}).get('value', 'N/A')}")
        print(f"  Target storage account  : {output.get('target_storage_account', {}).get('value', 'N/A')}")
        print(f"  Initiative name         : {output.get('initiative_name', {}).get('value', 'N/A')}")
        print(f"  Policy assignment ID    : {output.get('policy_assignment_id', {}).get('value', 'N/A')}")
        print(f"\nGoal: Escalate from Resource Policy Contributor to Owner on the target")
        print(f"      resource group and read the flag from the private storage blob.")
