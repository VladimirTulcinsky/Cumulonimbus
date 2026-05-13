from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):

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

    def configure_application(self, tf_output: dict) -> None:
        self.pretty_print_tf_output(tf_output)

    def pretty_print_tf_output(self, tf_output: dict) -> None:
        print("\n=== Logic App Hardcoded Credentials Lab ===")
        print(f"  Attacker UPN     : {tf_output.get('attacker_upn', {}).get('value', 'N/A')}")
        print(f"  Attacker password: {tf_output.get('attacker_password', {}).get('value', 'N/A')}")
        print(f"  Workflow name    : {tf_output.get('workflow_name', {}).get('value', 'N/A')}")
        print(f"  Resource group   : {tf_output.get('resource_group_name', {}).get('value', 'N/A')}")
        print("\nLogin as the attacker:")
        print("  az login --username <upn> --password <password>")
        print("\nGoal: Retrieve the flag from the Logic App workflow definition.")
