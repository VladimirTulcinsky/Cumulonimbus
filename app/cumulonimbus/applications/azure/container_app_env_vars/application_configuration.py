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

    mitre_ttps = [
        {"id": "T1552.001", "name": "Unsecured Credentials: Credentials in Files", "url": "https://attack.mitre.org/techniques/T1552/001/"},
        {"id": "T1083", "name": "File and Directory Discovery", "url": "https://attack.mitre.org/techniques/T1083/"},
    ]

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  Attacker Client ID     : {output.get('attacker_client_id', {}).get('value', 'N/A')}")
        print(f"  Attacker Client Secret : {output.get('attacker_client_secret', {}).get('value', 'N/A')}")
        print(f"  Resource Group         : {output.get('resource_group_name', {}).get('value', 'N/A')}")
        print(f"  Container App Name     : {output.get('container_app_name', {}).get('value', 'N/A')}")
        print(f"  Container App FQDN     : {output.get('container_app_fqdn', {}).get('value', 'N/A')}")
        print("\nGoal: Inspect the Container App definition to find the flag stored in an environment variable.")
        self.print_mitre_ttps()
