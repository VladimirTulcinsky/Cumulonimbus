from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def get_flag(self) -> str:
        return "CUMULONIMBUS{P0l1cy_M3t4d4t4_S3cr3t_3xp0s3d}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "Azure Policy assignments can include a free-form metadata field. This field is stored unencrypted and is readable by anyone with Reader access.",
            2: "List the policy assignments scoped to the resource group to find the assignment name.",
            3: "Run: az policy assignment list --resource-group <rg> --query '[].{name:name,metadata:metadata}', then inspect the metadata field for the flag.",
        }

    mitre_ttps = [
        {"id": "T1552", "name": "Unsecured Credentials", "url": "https://attack.mitre.org/techniques/T1552/"},
        {"id": "T1083", "name": "File and Directory Discovery", "url": "https://attack.mitre.org/techniques/T1083/"},
    ]

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  Attacker Client ID      : {output.get('attacker_client_id', {}).get('value', 'N/A')}")
        print(f"  Attacker Client Secret  : {output.get('attacker_client_secret', {}).get('value', 'N/A')}")
        print(f"  Resource Group          : {output.get('resource_group_name', {}).get('value', 'N/A')}")
        print(f"  Policy Assignment Name  : {output.get('policy_assignment_name', {}).get('value', 'N/A')}")
        print("\nGoal: Read the policy assignment metadata to find the flag embedded by the platform team.")
        self.print_mitre_ttps()
