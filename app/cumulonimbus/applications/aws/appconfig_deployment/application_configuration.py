from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def get_flag(self) -> str:
        return "CUMULONIMBUS{AppC0nf1g_H0st3d_C0nf1g_3xp0s3d}"
    def get_hints(self) -> dict:
        return {
            1: "The IAM user has AppConfig read permissions. AWS AppConfig stores configuration data in hosted configuration versions.",
            2: "Find the application and configuration profile IDs, then retrieve the hosted configuration version content.",
            3: "Run: aws appconfig list-applications, aws appconfig list-configuration-profiles --application-id <id>, then aws appconfig get-hosted-configuration-version --application-id <id> --configuration-profile-id <id> --version-number 1 /tmp/config.json && cat /tmp/config.json",
        }

    mitre_ttps = [
        {"id": "T1552", "name": "Unsecured Credentials", "url": "https://attack.mitre.org/techniques/T1552/"},
        {"id": "T1083", "name": "File and Directory Discovery", "url": "https://attack.mitre.org/techniques/T1083/"},
    ]

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  Access Key ID          : {output.get('attacker_access_key_id', {}).get('value', 'N/A')}")
        print(f"  Secret Access Key      : {output.get('attacker_secret_access_key', {}).get('value', 'N/A')}")
        print(f"  Application ID         : {output.get('application_id', {}).get('value', 'N/A')}")
        print(f"  Application Name       : {output.get('application_name', {}).get('value', 'N/A')}")
        print(f"  Configuration Profile  : {output.get('configuration_profile_id', {}).get('value', 'N/A')}")
        print("\nGoal: Download the AppConfig hosted configuration version and find the flag embedded in the JSON.")
        self.print_mitre_ttps()
