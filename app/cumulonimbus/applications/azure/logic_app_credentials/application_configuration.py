from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1552.001", "name": "Unsecured Credentials: Credentials in Files", "url": "https://attack.mitre.org/techniques/T1552/001/"},
        {"id": "T1580", "name": "Cloud Infrastructure Discovery", "url": "https://attack.mitre.org/techniques/T1580/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
    ]

    def get_flag(self) -> str:
        return "CUMULONIMBUS{L0g1c_App_H4rdcod3d_Cr3d3nt14ls}"

    def get_difficulty(self) -> str:
        return "Intermediate"

    def get_hints(self) -> dict:
        return {
            1: "Logic App workflow definitions are stored in ARM and include the full definition of every action — including any hardcoded values in HTTP connector headers.",
            2: "Use `az logic workflow show --name <workflow> --resource-group <rg>` to retrieve the full workflow JSON definition.",
            3: "Inspect the `actions` section of the workflow definition. Look at the HTTP action headers for an Authorization value containing the flag.",
        }

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  Attacker UPN     : {output.get('attacker_upn', {}).get('value', 'N/A')}")
        print(f"  Attacker password: {output.get('attacker_password', {}).get('value', 'N/A')}")
        print(f"  Workflow name    : {output.get('workflow_name', {}).get('value', 'N/A')}")
        print(f"  Resource group   : {output.get('resource_group_name', {}).get('value', 'N/A')}")
        print("\nLogin as the attacker:")
        print("  az login --username <upn> --password <password>")
        print("\nGoal: Retrieve the flag from the Logic App workflow definition.")
        self.print_mitre_ttps()