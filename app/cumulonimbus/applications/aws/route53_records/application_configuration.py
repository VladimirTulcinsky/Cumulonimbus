from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def get_flag(self) -> str:
        return "CUMULONIMBUS{R0ut353_TXT_R3c0rd_S3cr3ts}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "Route53 hosted zones can contain many record types. Some are used for verification or configuration purposes.",
            2: "Try listing all resource record sets in the hosted zone — the flag may be stored in a TXT record.",
            3: "Run: aws route53 list-hosted-zones, then: aws route53 list-resource-record-sets --hosted-zone-id <zone-id>",
        }

    def configure_application(self, tf_output: dict) -> None:
        self.pretty_print_tf_output(tf_output)

    def pretty_print_tf_output(self, tf_output: dict) -> None:
        print("\n=== Route53 Records Lab ===")
        print(f"  Access Key ID     : {tf_output.get('attacker_access_key_id', {}).get('value', 'N/A')}")
        print(f"  Secret Access Key : {tf_output.get('attacker_secret_access_key', {}).get('value', 'N/A')}")
        print(f"  Hosted Zone ID    : {tf_output.get('hosted_zone_id', {}).get('value', 'N/A')}")
        print(f"  Hosted Zone Name  : {tf_output.get('hosted_zone_name', {}).get('value', 'N/A')}")
        print("\nGoal: Enumerate the Route53 hosted zone and retrieve the flag hidden in a DNS record.")
