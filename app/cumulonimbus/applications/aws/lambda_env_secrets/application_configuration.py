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
            1: "You have lambda:ListFunctions and lambda:GetFunction. Inspect the function configuration — Lambda environment variables are returned in plaintext.",
            2: "Run: aws lambda list-functions --profile attacker to find the target function, then aws lambda get-function-configuration --function-name <name> --profile attacker",
            3: "The environment variables are under .Environment.Variables in the JSON response. Look for SECRET_API_KEY.",
        }

    def get_flag(self):
        return "CUMULONIMBUS{L4mbd4_3nv_S3cr3ts_Pl41nt3xt}"

    def pretty_print_tf_output(self, app_id, output):
        if not output:
            return
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] aws_access_key_id     : " + output["attacker_aws_access_key_id"]["value"])
        print("[2] aws_secret_access_key : " + output["attacker_aws_secret_access_key"]["value"])
        print("[3] function_name         : " + output["function_name"]["value"])
        print("")
        print("Configure the attacker profile, then inspect the function:")
        print("  aws configure --profile attacker")
        print("  aws lambda get-function-configuration --function-name '{}' --profile attacker".format(
            output["function_name"]["value"]))
        self.print_mitre_ttps()