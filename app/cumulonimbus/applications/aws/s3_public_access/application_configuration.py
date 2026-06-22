from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1530", "name": "Data from Cloud Storage", "url": "https://attack.mitre.org/techniques/T1530/"},
        {"id": "T1619", "name": "Cloud Storage Object Discovery", "url": "https://attack.mitre.org/techniques/T1619/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
    ]
    def configure_application(self, **kwargs):
        pass
    def get_hints(self):
        return {
            1: "Enumerate S3 buckets with your IAM credentials: aws s3 ls. Then check whether any bucket is publicly accessible without authentication.",
            2: "Use 'aws s3 ls s3://<bucket-name> --no-sign-request' — the --no-sign-request flag sends the request anonymously, bypassing your IAM identity.",
            3: "Download any object from the public bucket: aws s3 cp s3://<bucket-name>/flag.txt - --no-sign-request",
        }

    def get_flag(self):
        return "CUMULONIMBUS{S3_Publ1c_Acc3ss_Bl0ck_D1sabl3d}"

    def pretty_print_tf_output(self, app_id, output):
        if not output:
            return
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] aws_access_key_id     : " + output["attacker_aws_access_key_id"]["value"])
        print("[2] aws_secret_access_key : " + output["attacker_aws_secret_access_key"]["value"])
        print("[3] bucket_name           : " + output["bucket_name"]["value"])
        print("")
        print("Configure the attacker profile, then enumerate:")
        print("  aws configure --profile attacker")
        print("  aws s3 ls --profile attacker")
        self.print_mitre_ttps()