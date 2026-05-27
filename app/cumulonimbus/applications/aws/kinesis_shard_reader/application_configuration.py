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

    mitre_ttps = [
        {"id": "T1530", "name": "Data from Cloud Storage", "url": "https://attack.mitre.org/techniques/T1530/"},
        {"id": "T1619", "name": "Cloud Storage Object Discovery", "url": "https://attack.mitre.org/techniques/T1619/"},
    ]

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  Access Key ID     : {output.get('attacker_access_key_id', {}).get('value', 'N/A')}")
        print(f"  Secret Access Key : {output.get('attacker_secret_access_key', {}).get('value', 'N/A')}")
        print(f"  Stream Name       : {output.get('stream_name', {}).get('value', 'N/A')}")
        print("\nGoal: Read records from the Kinesis Data Stream shard and decode the flag.")
        self.print_mitre_ttps()
