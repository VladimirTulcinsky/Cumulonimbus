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

    def configure_application(self, tf_output: dict) -> None:
        self.pretty_print_tf_output(tf_output)

    def pretty_print_tf_output(self, tf_output: dict) -> None:
        print("\n=== DynamoDB Scan Lab ===")
        print(f"  Access Key ID     : {tf_output.get('attacker_access_key_id', {}).get('value', 'N/A')}")
        print(f"  Secret Access Key : {tf_output.get('attacker_secret_access_key', {}).get('value', 'N/A')}")
        print(f"  Table Name        : {tf_output.get('table_name', {}).get('value', 'N/A')}")
        print("\nGoal: Scan the DynamoDB table and retrieve the flag stored in a table item.")
