from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):

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

    def configure_application(self, tf_output: dict) -> None:
        self.pretty_print_tf_output(tf_output)

    def pretty_print_tf_output(self, tf_output: dict) -> None:
        print("\n=== S3 Object Public ACL Lab ===")
        print(f"  Bucket name   : {tf_output.get('bucket_name', {}).get('value', 'N/A')}")
        print(f"  Flag URL      : {tf_output.get('flag_object_url', {}).get('value', 'N/A')}")
        print("\nGoal: Access the publicly readable S3 object without any AWS credentials.")
