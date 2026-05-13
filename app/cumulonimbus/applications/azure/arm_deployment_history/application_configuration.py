from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def configure_application(self, **kwargs):
        pass

    def get_difficulty(self):
        return "Intermediate"

    def get_hints(self):
        return {
            1: "Log in as the attacker and list deployments in the resource group: az deployment group list --resource-group <rg>. Reader includes Microsoft.Resources/deployments/read.",
            2: "Show the deployment details: az deployment group show --resource-group <rg> --name app-infra-v1. Look inside .properties.parameters for parameter values.",
            3: "The adminApiKey parameter was declared as type 'string' instead of 'secureString'. Its value is exposed in plaintext: az deployment group show ... --query properties.parameters.adminApiKey.value -o tsv",
        }

    def get_flag(self):
        return "CUMULONIMBUS{4RM_D3pl0yment_H1st0ry_Pl41nt3xt}"

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] Attacker username : " + output["attacker_username"]["value"])
        print("[2] Attacker password : " + output["attacker_password"]["value"])
        print("[3] Resource group    : " + output["resource_group_name"]["value"])
        print("[4] Deployment name   : " + output["deployment_name"]["value"])
        print("")
        print("Login and inspect deployment history:")
        print("  az login -u '{}' -p '<password>'".format(output["attacker_username"]["value"]))
        print("  az deployment group show --resource-group '{}' --name '{}' --query properties.parameters".format(
            output["resource_group_name"]["value"], output["deployment_name"]["value"]))
