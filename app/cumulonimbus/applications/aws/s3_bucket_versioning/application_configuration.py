from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1530", "name": "Data from Cloud Storage", "url": "https://attack.mitre.org/techniques/T1530/"},
        {"id": "T1619", "name": "Cloud Storage Object Discovery", "url": "https://attack.mitre.org/techniques/T1619/"},
        {"id": "T1552.001", "name": "Unsecured Credentials: Credentials in Files", "url": "https://attack.mitre.org/techniques/T1552/001/"},
    ]
    def configure_application(self, **kwargs):
        pass

    def get_difficulty(self):
        return "Beginner"

    def get_hints(self):
        return {
            1: "The current version of app/config.json is a delete marker — the object appears gone. But versioning keeps every previous version. Try: aws s3api list-object-versions --bucket <bucket>",
            2: "The output shows multiple VersionIds for app/config.json. Retrieve an older version with: aws s3api get-object --bucket <bucket> --key app/config.json --version-id <id> out.json",
            3: "The first version (earliest LastModified) contains the original config with the secret_key field. Download it and read out.json.",
        }

    def get_flag(self):
        return "CUMULONIMBUS{S3_V3rs10n1ng_D3l3t3d_0bj3cts}"

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
        print("Configure the attacker profile and list object versions:")
        print("  aws configure --profile attacker  # region: eu-west-1")
        print("  aws s3api list-object-versions --bucket '{}' --profile attacker".format(
            output["bucket_name"]["value"]))
        self.print_mitre_ttps()