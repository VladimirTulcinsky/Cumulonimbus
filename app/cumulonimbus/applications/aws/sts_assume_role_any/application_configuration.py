from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
        {"id": "T1580", "name": "Cloud Infrastructure Discovery", "url": "https://attack.mitre.org/techniques/T1580/"},
        {"id": "T1548", "name": "Privilege Escalation via Cloud Services", "url": "https://attack.mitre.org/techniques/T1548/"},
    ]

    def get_flag(self) -> str:
        return "CUMULONIMBUS{STS_Assum3_R0l3_W1ldcard_Pr1ncipal}"
    def get_hints(self) -> dict:
        return {
            1: "The environment has an IAM role with a broad trust policy. Start by listing IAM roles available in the account.",
            2: "Use `aws iam list-roles` to find the cumulonimbus role, then try `aws sts assume-role` — check the Principal field in the trust policy.",
            3: "After assuming the role, use the returned temporary credentials to read the SSM parameter at /cumulonimbus/sts_assume_role_any/flag.",
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
        print(f"  Target role ARN   : {output.get('target_role_arn', {}).get('value', 'N/A')}")
        print("\nConfigure the attacker profile:")
        print("  aws configure --profile attacker   # region: eu-west-1")
        print("\nGoal: Assume the misconfigured role and retrieve the flag from SSM.")
        self.print_mitre_ttps()