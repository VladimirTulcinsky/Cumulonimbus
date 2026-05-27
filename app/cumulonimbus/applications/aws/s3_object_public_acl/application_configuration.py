from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1530", "name": "Data from Cloud Storage", "url": "https://attack.mitre.org/techniques/T1530/"},
        {"id": "T1619", "name": "Cloud Storage Object Discovery", "url": "https://attack.mitre.org/techniques/T1619/"},
    ]

    def get_flag(self) -> str:
        return "CUMULONIMBUS{S3_0bj3ct_ACL_Publ1c_R3ad}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "The S3 bucket blocks public bucket policies, but individual objects can still have public ACLs. Try listing what objects exist in the bucket.",
            2: "Use `aws s3 ls s3://<bucket>/ --recursive` or enumerate common key prefixes. One object has a public-read ACL.",
            3: "The flag object is at `public/release-notes.txt`. Fetch it directly: `curl https://<bucket>.s3.eu-west-1.amazonaws.com/public/release-notes.txt`",
        }

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  Bucket name   : {output.get('bucket_name', {}).get('value', 'N/A')}")
        print(f"  Flag URL      : {output.get('flag_object_url', {}).get('value', 'N/A')}")
        print("\nGoal: Access the publicly readable S3 object without any AWS credentials.")
        self.print_mitre_ttps()