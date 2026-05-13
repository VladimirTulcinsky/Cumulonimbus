from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def get_flag(self) -> str:
        return "CUMULONIMBUS{C0nt41n3r_App_Env_V4rs_3xp0s3d}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "Azure Container Apps store configuration in their template definition. Environment variables are part of this.",
            2: "A Reader on the resource group can read the full Container App resource definition including environment variables.",
            3: "Run: az containerapp show --name <app-name> --resource-group <rg> --query 'properties.template.containers[0].env'",
        }

    def configure_application(self, tf_output: dict) -> None:
        self.pretty_print_tf_output(tf_output)

    def pretty_print_tf_output(self, tf_output: dict) -> None:
        print("\n=== Container App Env Vars Lab ===")
        print(f"  Attacker Client ID     : {tf_output.get('attacker_client_id', {}).get('value', 'N/A')}")
        print(f"  Attacker Client Secret : {tf_output.get('attacker_client_secret', {}).get('value', 'N/A')}")
        print(f"  Resource Group         : {tf_output.get('resource_group_name', {}).get('value', 'N/A')}")
        print(f"  Container App Name     : {tf_output.get('container_app_name', {}).get('value', 'N/A')}")
        print(f"  Container App FQDN     : {tf_output.get('container_app_fqdn', {}).get('value', 'N/A')}")
        print("\nGoal: Inspect the Container App definition to find the flag stored in an environment variable.")
