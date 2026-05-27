from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
        {"id": "T1528", "name": "Steal Application Access Token", "url": "https://attack.mitre.org/techniques/T1528/"},
        {"id": "T1530", "name": "Data from Cloud Storage", "url": "https://attack.mitre.org/techniques/T1530/"},
    ]

    def get_flag(self) -> str:
        return "CUMULONIMBUS{C0gn1t0_Un4uth_1d3nt1ty_AWS_Cr3ds}"

    def get_difficulty(self) -> str:
        return "Intermediate"

    def get_hints(self) -> dict:
        return {
            1: "The Cognito Identity Pool allows unauthenticated (guest) identities. You can obtain temporary AWS credentials without any login.",
            2: "Use `aws cognito-identity get-id --identity-pool-id <id> --account-id <account>` to get an identity ID, then `get-credentials-for-identity` to exchange it for AWS credentials.",
            3: "The temporary credentials have S3 read access. Use them to read s3://<bucket>/secret/flag.txt — the bucket name is in the lab output.",
        }

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("\n=== Cognito Identity Pool Lab ===")
        print(f"  Identity pool ID : {output.get('identity_pool_id', {}).get('value', 'N/A')}")
        print(f"  Account ID       : {output.get('account_id', {}).get('value', 'N/A')}")
        print(f"  Region           : {output.get('region', {}).get('value', 'N/A')}")
        print(f"  Flag bucket      : {output.get('flag_bucket', {}).get('value', 'N/A')}")
        print(f"  Flag object      : {output.get('flag_object_key', {}).get('value', 'N/A')}")
        print("\nGoal: Obtain unauthenticated AWS credentials via Cognito and read the flag from S3.")
        self.print_mitre_ttps()