from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):

    def get_flag(self) -> str:
        return "CUMULONIMBUS{STS_Assum3_R0l3_W1ldcard_Pr1ncipal}"

    def get_difficulty(self) -> str:
        return "Intermediate"

    def get_hints(self) -> dict:
        return {
            1: "The environment has an IAM role with a broad trust policy. Start by listing IAM roles available in the account.",
            2: "Use `aws iam list-roles` to find the cumulonimbus role, then try `aws sts assume-role` — check the Principal field in the trust policy.",
            3: "After assuming the role, use the returned temporary credentials to read the SSM parameter at /cumulonimbus/sts_assume_role_any/flag.",
        }

    def configure_application(self, tf_output: dict) -> None:
        self.pretty_print_tf_output(tf_output)

    def pretty_print_tf_output(self, tf_output: dict) -> None:
        print("\n=== STS Assume Role Any Lab ===")
        print(f"  Attacker user     : {tf_output.get('attacker_username', {}).get('value', 'N/A')}")
        print(f"  Access key ID     : {tf_output.get('attacker_access_key_id', {}).get('value', 'N/A')}")
        print(f"  Secret access key : {tf_output.get('attacker_secret_access_key', {}).get('value', 'N/A')}")
        print(f"  Target role ARN   : {tf_output.get('target_role_arn', {}).get('value', 'N/A')}")
        print("\nConfigure the attacker profile:")
        print("  aws configure --profile attacker   # region: eu-west-1")
        print("\nGoal: Assume the misconfigured role and retrieve the flag from SSM.")
