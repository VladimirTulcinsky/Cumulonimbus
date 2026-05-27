from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1552.001", "name": "Unsecured Credentials: Credentials in Files", "url": "https://attack.mitre.org/techniques/T1552/001/"},
        {"id": "T1580", "name": "Cloud Infrastructure Discovery", "url": "https://attack.mitre.org/techniques/T1580/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
    ]

    def get_flag(self) -> str:
        return "CUMULONIMBUS{App_C0nf1g_D4t4_R34d3r_Enum}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "Azure App Configuration stores key-value pairs accessible to any identity with App Configuration Data Reader. Try listing all keys in the store.",
            2: "Use `az appconfig kv list --name <store> --auth-mode login` to list all key-values in the configuration store.",
            3: "Look for the `secrets/api-key` key — its value contains the flag.",
        }

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  Attacker UPN        : {output.get('attacker_upn', {}).get('value', 'N/A')}")
        print(f"  Attacker password   : {output.get('attacker_password', {}).get('value', 'N/A')}")
        print(f"  Config store name   : {output.get('config_store_name', {}).get('value', 'N/A')}")
        print(f"  Resource group      : {output.get('resource_group_name', {}).get('value', 'N/A')}")
        print("\nLogin as the attacker:")
        print("  az login --username <upn> --password <password>")
        print("\nGoal: Enumerate all key-values in the App Configuration store and find the flag.")
        self.print_mitre_ttps()