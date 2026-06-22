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
            1: "You have ssm:DescribeParameters. Use it to enumerate all parameter names, then check which paths your identity can read with GetParametersByPath.",
            2: "Run: aws ssm get-parameters-by-path --path /cumulonimbus/ --recursive --with-decryption --profile attacker",
            3: "The flag is in a SecureString parameter named /cumulonimbus/production/flag. The --with-decryption flag (plus kms:Decrypt) decrypts SecureString values inline.",
        }

    def get_flag(self):
        return "CUMULONIMBUS{SSM_P4r4m3t3r_P4th_W1ldcard}"

    def pretty_print_tf_output(self, app_id, output):
        if not output:
            return
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] aws_access_key_id     : " + output["attacker_aws_access_key_id"]["value"])
        print("[2] aws_secret_access_key : " + output["attacker_aws_secret_access_key"]["value"])
        print("[3] parameter_path_prefix : " + output["parameter_path_prefix"]["value"])
        print("")
        print("Configure the attacker profile and enumerate parameters:")
        print("  aws configure --profile attacker  # region: eu-west-1")
        print("  aws ssm get-parameters-by-path --path /cumulonimbus/ --recursive --with-decryption --profile attacker")
        self.print_mitre_ttps()