from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1552.001", "name": "Unsecured Credentials: Credentials in Files", "url": "https://attack.mitre.org/techniques/T1552/001/"},
        {"id": "T1580", "name": "Cloud Infrastructure Discovery", "url": "https://attack.mitre.org/techniques/T1580/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
    ]

    def get_flag(self) -> str:
        return "CUMULONIMBUS{App_S3rv1c3_Env_V4rs_3xp0s3d}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "App Service stores configuration as application settings. These can be read by identities with the right permissions — look at what your attacker account can do.",
            2: "The `Microsoft.Web/sites/config/list` action returns app settings in plaintext. Try using the Azure CLI: `az webapp config appsettings list`.",
            3: "Run `az webapp config appsettings list --name <app> --resource-group <rg>` with the attacker credentials. Look for the SECRET_FLAG setting.",
        }

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  Attacker UPN         : {output.get('attacker_upn', {}).get('value', 'N/A')}")
        print(f"  Attacker password    : {output.get('attacker_password', {}).get('value', 'N/A')}")
        print(f"  App Service name     : {output.get('app_service_name', {}).get('value', 'N/A')}")
        print(f"  Resource group       : {output.get('resource_group_name', {}).get('value', 'N/A')}")
        print(f"  Subscription ID      : {output.get('subscription_id', {}).get('value', 'N/A')}")
        print("\nLogin as the attacker:")
        print("  az login --username <upn> --password <password>")
        print("\nGoal: Retrieve the flag from the App Service application settings.")
        self.print_mitre_ttps()