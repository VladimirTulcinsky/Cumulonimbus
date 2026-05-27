from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def get_flag(self) -> str:
        return "CUMULONIMBUS{ADF_L1nk3d_S3rv1c3_Cl34rt3xt_K3y}"

    def get_difficulty(self) -> str:
        return "Intermediate"

    def get_hints(self) -> dict:
        return {
            1: "Azure Data Factory stores connection details for linked services in its ARM definition. Credentials not backed by Key Vault are stored in cleartext.",
            2: "A Reader on the resource group can enumerate all linked services in a Data Factory instance.",
            3: "Run: az datafactory linked-service list --factory-name <name> --resource-group <rg>, then: az datafactory linked-service show --factory-name <name> --linked-service-name DataLakeConnection --resource-group <rg> --query 'typeProperties.connectionString'",
        }

    mitre_ttps = [
        {"id": "T1552", "name": "Unsecured Credentials", "url": "https://attack.mitre.org/techniques/T1552/"},
        {"id": "T1083", "name": "File and Directory Discovery", "url": "https://attack.mitre.org/techniques/T1083/"},
    ]

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("\n=== Data Factory Linked Service Lab ===")
        print(f"  Attacker Client ID     : {output.get('attacker_client_id', {}).get('value', 'N/A')}")
        print(f"  Attacker Client Secret : {output.get('attacker_client_secret', {}).get('value', 'N/A')}")
        print(f"  Resource Group         : {output.get('resource_group_name', {}).get('value', 'N/A')}")
        print(f"  Data Factory Name      : {output.get('data_factory_name', {}).get('value', 'N/A')}")
        print(f"  Linked Service Name    : {output.get('linked_service_name', {}).get('value', 'N/A')}")
        print("\nGoal: Read the Data Factory linked service definition to extract the cleartext storage account key.")
        self.print_mitre_ttps()
