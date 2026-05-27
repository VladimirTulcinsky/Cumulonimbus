from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract
import cumulonimbus.core.utils as utils
import os


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1552.005", "name": "Unsecured Credentials: Cloud Instance Metadata API", "url": "https://attack.mitre.org/techniques/T1552/005/"},
        {"id": "T1530", "name": "Data from Cloud Storage", "url": "https://attack.mitre.org/techniques/T1530/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
    ]
    def configure_application(self, **kwargs):
        pass

    def get_difficulty(self):
        return "Intermediate"

    def get_hints(self):
        return {
            1: "You have Reader on the resource group. Use 'az keyvault list' to discover Key Vaults, then check whether your user has any access policies on them.",
            2: "The vault uses access policy mode rather than RBAC. Try 'az keyvault secret list --vault-name <name>' — the policy may grant you more than expected.",
            3: "az keyvault secret show --vault-name <name> --name flag",
        }

    def get_flag(self):
        return "CUMULONIMBUS{K3yV4ult_4cc3ss_P0l1cy_T00_Br04d}"

    def pretty_print_tf_output(self, app_id, output):
        if not output:
            return
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] Attacker username : " + output["attacker_username"]["value"])
        print("[2] Attacker password : " + output["attacker_password"]["value"])
        print("[3] Key Vault name    : " + output["key_vault_name"]["value"])
        print("[4] Key Vault URI     : " + output["key_vault_uri"]["value"])
        print("[5] Resource group    : " + output["resource_group_name"]["value"])
        self.print_mitre_ttps()