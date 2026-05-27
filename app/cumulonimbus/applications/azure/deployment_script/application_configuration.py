from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def get_flag(self) -> str:
        return "CUMULONIMBUS{D3pl0ym3nt_Scr1pt_0utput_3xp0s3d}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "Azure Deployment Scripts run scripts during infrastructure provisioning and can store outputs in the resource definition.",
            2: "The outputs of a Deployment Script resource are accessible to anyone with Reader on the resource group.",
            3: "Run: az deployment-scripts list --resource-group <rg>, then: az deployment-scripts show --name <name> --resource-group <rg> --query outputs",
        }

    mitre_ttps = [
        {"id": "T1552.001", "name": "Unsecured Credentials: Credentials in Files", "url": "https://attack.mitre.org/techniques/T1552/001/"},
        {"id": "T1530", "name": "Data from Cloud Storage", "url": "https://attack.mitre.org/techniques/T1530/"},
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
        print(f"  Deployment Script Name : {output.get('deployment_script_name', {}).get('value', 'N/A')}")
        print("\nGoal: Retrieve the Deployment Script outputs to find the flag.")
        self.print_mitre_ttps()
