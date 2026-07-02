from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1552.001", "name": "Unsecured Credentials: Credentials in Files", "url": "https://attack.mitre.org/techniques/T1552/001/"},
        {"id": "T1580", "name": "Cloud Infrastructure Discovery", "url": "https://attack.mitre.org/techniques/T1580/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
    ]

    def get_flag(self) -> str:
        return "CUMULONIMBUS{Glu3_J0b_S3cr3ts_1n_4rgum3nts}"
    def get_hints(self) -> dict:
        return {
            1: "AWS Glue jobs store their configuration in `DefaultArguments`. These are returned in plaintext by `glue:GetJob`.",
            2: "Use `aws glue list-jobs` to find the job name, then `aws glue get-job --job-name <name>` to retrieve the full configuration.",
            3: "The flag is in the `--api-key` argument inside `DefaultArguments` of the Glue job definition.",
        }

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  Attacker user     : {output.get('attacker_username', {}).get('value', 'N/A')}")
        print(f"  Access key ID     : {output.get('attacker_access_key_id', {}).get('value', 'N/A')}")
        print(f"  Secret access key : {output.get('attacker_secret_access_key', {}).get('value', 'N/A')}")
        print(f"  Glue job name     : {output.get('glue_job_name', {}).get('value', 'N/A')}")
        print("\nConfigure the attacker profile:")
        print("  aws configure --profile attacker   # region: eu-west-1")
        print("\nGoal: Retrieve the flag from the Glue job's DefaultArguments.")
        self.print_mitre_ttps()