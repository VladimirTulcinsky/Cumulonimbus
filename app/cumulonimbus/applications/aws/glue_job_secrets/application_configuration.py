from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):

    def get_flag(self) -> str:
        return "CUMULONIMBUS{Glu3_J0b_S3cr3ts_1n_4rgum3nts}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "AWS Glue jobs store their configuration in `DefaultArguments`. These are returned in plaintext by `glue:GetJob`.",
            2: "Use `aws glue list-jobs` to find the job name, then `aws glue get-job --job-name <name>` to retrieve the full configuration.",
            3: "The flag is in the `--api-key` argument inside `DefaultArguments` of the Glue job definition.",
        }

    def configure_application(self, tf_output: dict) -> None:
        self.pretty_print_tf_output(tf_output)

    def pretty_print_tf_output(self, tf_output: dict) -> None:
        print("\n=== Glue Job Secrets Lab ===")
        print(f"  Attacker user     : {tf_output.get('attacker_username', {}).get('value', 'N/A')}")
        print(f"  Access key ID     : {tf_output.get('attacker_access_key_id', {}).get('value', 'N/A')}")
        print(f"  Secret access key : {tf_output.get('attacker_secret_access_key', {}).get('value', 'N/A')}")
        print(f"  Glue job name     : {tf_output.get('glue_job_name', {}).get('value', 'N/A')}")
        print("\nConfigure the attacker profile:")
        print("  aws configure --profile attacker   # region: eu-west-1")
        print("\nGoal: Retrieve the flag from the Glue job's DefaultArguments.")
