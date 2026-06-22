from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1552.001", "name": "Unsecured Credentials: Credentials in Files", "url": "https://attack.mitre.org/techniques/T1552/001/"},
        {"id": "T1580", "name": "Cloud Infrastructure Discovery", "url": "https://attack.mitre.org/techniques/T1580/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
    ]
    def configure_application(self, **kwargs):
        pass
    def get_hints(self):
        return {
            1: "You have ec2:DescribeInstances and ec2:DescribeInstanceAttribute. Use DescribeInstances to find the instance ID, then request the userData attribute.",
            2: "Run: aws ec2 describe-instance-attribute --instance-id <id> --attribute userData --profile attacker — the value is base64-encoded.",
            3: "Decode the user data: aws ec2 describe-instance-attribute --instance-id <id> --attribute userData --profile attacker --query UserData.Value --output text | base64 -d",
        }

    def get_flag(self):
        return "CUMULONIMBUS{3c2_Us3rD4t4_S3cr3ts_3xp0s3d}"

    def pretty_print_tf_output(self, app_id, output):
        if not output:
            return
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] aws_access_key_id     : " + output["attacker_aws_access_key_id"]["value"])
        print("[2] aws_secret_access_key : " + output["attacker_aws_secret_access_key"]["value"])
        print("[3] instance_id           : " + output["instance_id"]["value"])
        print("")
        print("Configure the attacker profile, then read user data:")
        print("  aws configure --profile attacker  # region: eu-west-1")
        print("  aws ec2 describe-instance-attribute --instance-id '{}' --attribute userData --profile attacker --query UserData.Value --output text | base64 -d".format(
            output["instance_id"]["value"]))
        self.print_mitre_ttps()