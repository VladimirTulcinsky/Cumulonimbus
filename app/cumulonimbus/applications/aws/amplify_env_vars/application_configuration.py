from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def get_flag(self) -> str:
        return "CUMULONIMBUS{4mpl1fy_App_3nv_V4rs_3xp0s3d}"
    def get_hints(self) -> dict:
        return {
            1: "The IAM user has Amplify read permissions. AWS Amplify apps store environment variables in the app definition.",
            2: "List Amplify apps to find the target, then retrieve the full app details including environment variables.",
            3: "Run: aws amplify list-apps, then: aws amplify get-app --app-id <app-id> --query 'app.environmentVariables'",
        }

    mitre_ttps = [
        {"id": "T1552.001", "name": "Unsecured Credentials: Credentials in Files", "url": "https://attack.mitre.org/techniques/T1552/001/"},
        {"id": "T1083", "name": "File and Directory Discovery", "url": "https://attack.mitre.org/techniques/T1083/"},
        {"id": "T1530", "name": "Data from Cloud Storage", "url": "https://attack.mitre.org/techniques/T1530/"},
    ]

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  Access Key ID     : {output.get('attacker_access_key_id', {}).get('value', 'N/A')}")
        print(f"  Secret Access Key : {output.get('attacker_secret_access_key', {}).get('value', 'N/A')}")
        print(f"  Amplify App ID    : {output.get('amplify_app_id', {}).get('value', 'N/A')}")
        print(f"  Amplify App Name  : {output.get('amplify_app_name', {}).get('value', 'N/A')}")
        print("\nGoal: Retrieve the Amplify app definition and read the flag from environment variables.")
        self.print_mitre_ttps()
