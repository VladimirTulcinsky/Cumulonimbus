from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):

    def get_flag(self) -> str:
        return "CUMULONIMBUS{St3pFunct10ns_3x3cut10n_H1st0ry_L34k}"

    def get_difficulty(self) -> str:
        return "Intermediate"

    def get_hints(self) -> dict:
        return {
            1: "Step Functions stores the full input and output of every execution in its execution history. This history is readable by anyone with states:GetExecutionHistory.",
            2: "Use `aws stepfunctions list-state-machines` to find the machine ARN, then `aws stepfunctions list-executions` to find past execution ARNs.",
            3: "Run `aws stepfunctions get-execution-history --execution-arn <arn>` and look at the `executionStarted` event's `input` field — it contains the flag.",
        }

    def configure_application(self, tf_output: dict) -> None:
        self.pretty_print_tf_output(tf_output)

    def pretty_print_tf_output(self, tf_output: dict) -> None:
        print("\n=== Step Functions Execution History Lab ===")
        print(f"  Attacker user       : {tf_output.get('attacker_username', {}).get('value', 'N/A')}")
        print(f"  Access key ID       : {tf_output.get('attacker_access_key_id', {}).get('value', 'N/A')}")
        print(f"  Secret access key   : {tf_output.get('attacker_secret_access_key', {}).get('value', 'N/A')}")
        print(f"  State machine ARN   : {tf_output.get('state_machine_arn', {}).get('value', 'N/A')}")
        print("\nConfigure the attacker profile:")
        print("  aws configure --profile attacker   # region: eu-west-1")
        print("\nGoal: Retrieve the flag from a past Step Functions execution's input data.")
