from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):

    def get_flag(self) -> str:
        return "CUMULONIMBUS{C0nt41n3r_1nst4nc3_Pl41nt3xt_Env}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "Azure Container Instances expose their environment variables via ARM. A Reader on the resource group can inspect the container group definition.",
            2: "Use `az container show --name <name> --resource-group <rg>` to retrieve the container configuration including environment variables.",
            3: "Look for the `SECRET_FLAG` environment variable in the `environmentVariables` array of the container definition.",
        }

    def configure_application(self, tf_output: dict) -> None:
        self.pretty_print_tf_output(tf_output)

    def pretty_print_tf_output(self, tf_output: dict) -> None:
        print("\n=== Container Instance Environment Variables Lab ===")
        print(f"  Attacker UPN        : {tf_output.get('attacker_upn', {}).get('value', 'N/A')}")
        print(f"  Attacker password   : {tf_output.get('attacker_password', {}).get('value', 'N/A')}")
        print(f"  Container group     : {tf_output.get('container_group_name', {}).get('value', 'N/A')}")
        print(f"  Resource group      : {tf_output.get('resource_group_name', {}).get('value', 'N/A')}")
        print("\nLogin as the attacker:")
        print("  az login --username <upn> --password <password>")
        print("\nGoal: Retrieve the flag from the container's environment variables.")
