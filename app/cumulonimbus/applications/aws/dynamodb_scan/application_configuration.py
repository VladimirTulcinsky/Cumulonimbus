from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def get_flag(self) -> str:
        return "CUMULONIMBUS{Dyn4m0DB_Sc4n_D4t4_3xp0sur3}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "The IAM user has DynamoDB read permissions. Start by listing available tables.",
            2: "Once you find the table, scan all items — secrets stored in DynamoDB are not automatically encrypted at rest.",
            3: "Run: aws dynamodb list-tables, then: aws dynamodb scan --table-name <table-name>",
        }

    mitre_ttps = [
        {"id": "T1619", "name": "Cloud Storage Object Discovery", "url": "https://attack.mitre.org/techniques/T1619/"},
        {"id": "T1530", "name": "Data from Cloud Storage", "url": "https://attack.mitre.org/techniques/T1530/"},
    ]

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("\n=== DynamoDB Scan Lab ===")
        print(f"  Access Key ID     : {output.get('attacker_access_key_id', {}).get('value', 'N/A')}")
        print(f"  Secret Access Key : {output.get('attacker_secret_access_key', {}).get('value', 'N/A')}")
        print(f"  Table Name        : {output.get('table_name', {}).get('value', 'N/A')}")
        print("\nGoal: Scan the DynamoDB table and retrieve the flag stored in a table item.")
        self.print_mitre_ttps()
