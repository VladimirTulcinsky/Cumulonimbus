from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):

    def get_flag(self) -> str:
        return "CUMULONIMBUS{S3cr3t_1n_R3s0urc3_Gr0up_T4gs}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "Azure resource tags are visible to anyone with Reader on the resource. Engineers sometimes store credentials in tags for convenience.",
            2: "Use `az group list` to find the cumulonimbus resource group, then `az group show --name <rg>` to see all its tags.",
            3: "Look for the `service-principal-secret` tag on the resource group — it contains the flag.",
        }

    def configure_application(self, tf_output: dict) -> None:
        self.pretty_print_tf_output(tf_output)

    def pretty_print_tf_output(self, tf_output: dict) -> None:
        print("\n=== Resource Group Tags Lab ===")
        print(f"  Attacker UPN     : {tf_output.get('attacker_upn', {}).get('value', 'N/A')}")
        print(f"  Attacker password: {tf_output.get('attacker_password', {}).get('value', 'N/A')}")
        print(f"  Resource group   : {tf_output.get('resource_group_name', {}).get('value', 'N/A')}")
        print("\nLogin as the attacker:")
        print("  az login --username <upn> --password <password>")
        print("\nGoal: Retrieve the flag from the resource group's tags.")
