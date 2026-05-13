from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def get_flag(self) -> str:
        return "CUMULONIMBUS{AP1M_N4m3d_V4lu3_Pl41nt3xt}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "Azure API Management uses Named Values to store configuration data. These can be plaintext or secret.",
            2: "Non-secret Named Values are readable by anyone with Reader access on the resource group.",
            3: "Run: az apim nv list --service-name <apim-name> --resource-group <rg>, then: az apim nv show --service-name <apim-name> --resource-group <rg> --named-value-id flag-key --query value -o tsv",
        }

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("\n=== APIM Named Value Lab ===")
        print(f"  Attacker Client ID     : {output.get('attacker_client_id', {}).get('value', 'N/A')}")
        print(f"  Attacker Client Secret : {output.get('attacker_client_secret', {}).get('value', 'N/A')}")
        print(f"  Resource Group         : {output.get('resource_group_name', {}).get('value', 'N/A')}")
        print(f"  APIM Name              : {output.get('apim_name', {}).get('value', 'N/A')}")
        print(f"  Named Value ID         : {output.get('named_value_id', {}).get('value', 'N/A')}")
        print("\nGoal: Read the plaintext Named Value in Azure API Management to retrieve the flag.")
