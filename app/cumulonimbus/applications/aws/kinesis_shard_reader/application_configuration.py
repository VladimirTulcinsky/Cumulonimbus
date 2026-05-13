from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def get_flag(self) -> str:
        return "CUMULONIMBUS{K1n3s1s_Sh4rd_R3c0rd_L34k}"

    def get_difficulty(self) -> str:
        return "Intermediate"

    def get_hints(self) -> dict:
        return {
            1: "The IAM user has Kinesis read permissions. Start by listing streams and describing the target stream to find its shard IDs.",
            2: "To read records from Kinesis you need a shard iterator. Use TRIM_HORIZON to start from the oldest record in the shard.",
            3: "Run: aws kinesis list-streams, then get-shard-iterator with --shard-iterator-type TRIM_HORIZON, then aws kinesis get-records --shard-iterator <iterator>. Records are base64-encoded.",
        }

    def configure_application(self, tf_output: dict) -> None:
        self.pretty_print_tf_output(tf_output)

    def pretty_print_tf_output(self, tf_output: dict) -> None:
        print("\n=== Kinesis Shard Reader Lab ===")
        print(f"  Access Key ID     : {tf_output.get('attacker_access_key_id', {}).get('value', 'N/A')}")
        print(f"  Secret Access Key : {tf_output.get('attacker_secret_access_key', {}).get('value', 'N/A')}")
        print(f"  Stream Name       : {tf_output.get('stream_name', {}).get('value', 'N/A')}")
        print("\nGoal: Read records from the Kinesis Data Stream shard and decode the flag.")
