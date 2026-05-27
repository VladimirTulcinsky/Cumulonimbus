from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1021", "name": "Remote Services", "url": "https://attack.mitre.org/techniques/T1021/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
        {"id": "T1059", "name": "Command and Scripting Interpreter", "url": "https://attack.mitre.org/techniques/T1059/"},
        {"id": "T1570", "name": "Lateral Movement", "url": "https://attack.mitre.org/techniques/T1570/"},
    ]

    def get_flag(self) -> str:
        return "CUMULONIMBUS{SSM_S3ss10n_M4n4g3r_Sh3ll_4cc3ss}"

    def get_difficulty(self) -> str:
        return "Intermediate"

    def get_hints(self) -> dict:
        return {
            1: "Your attacker credentials include `ssm:StartSession`. This allows you to open an interactive shell on any EC2 instance that has the SSM Agent running — no SSH key required.",
            2: "Find the target instance with `aws ec2 describe-instances --query \"Reservations[*].Instances[*].{ID:InstanceId,Tags:Tags}\"`, then use `aws ssm start-session --target <instance-id>`.",
            3: "Once connected, run `sudo cat /root/flag.txt` to read the flag from the instance filesystem.",
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
        print(f"  Instance ID       : {output.get('instance_id', {}).get('value', 'N/A')}")
        print("\nConfigure the attacker profile:")
        print("  aws configure --profile attacker   # region: eu-west-1")
        print("\nNote: The Session Manager plugin for the AWS CLI must be installed.")
        print("  https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html")
        print("\nGoal: Open a shell on the EC2 instance via SSM and read /root/flag.txt.")
        self.print_mitre_ttps()