from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):

    def get_flag(self) -> str:
        return "CUMULONIMBUS{Cl0udF0rm4t10n_Outputs_Expos3_S3cr3ts}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "CloudFormation stacks can expose sensitive data. Try describing the stack that was deployed.",
            2: "Use `aws cloudformation describe-stacks --stack-name <name>` — pay attention to the Outputs section.",
            3: "Stack outputs are returned in plaintext by DescribeStacks, even when they contain secrets. Look for the ApiKey output.",
        }

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("\n=== CloudFormation Stack Lab ===")
        print(f"  Stack name        : {output.get('stack_name', {}).get('value', 'N/A')}")
        print(f"  Attacker user     : {output.get('attacker_username', {}).get('value', 'N/A')}")
        print(f"  Access key ID     : {output.get('attacker_access_key_id', {}).get('value', 'N/A')}")
        print(f"  Secret access key : {output.get('attacker_secret_access_key', {}).get('value', 'N/A')}")
        print("\nConfigure the attacker profile:")
        print("  aws configure --profile attacker   # region: eu-west-1")
        print("\nGoal: Retrieve the flag from the CloudFormation stack outputs.")
