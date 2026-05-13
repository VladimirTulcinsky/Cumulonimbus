from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def get_flag(self) -> str:
        return "CUMULONIMBUS{4mpl1fy_App_3nv_V4rs_3xp0s3d}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "The IAM user has Amplify read permissions. AWS Amplify apps store environment variables in the app definition.",
            2: "List Amplify apps to find the target, then retrieve the full app details including environment variables.",
            3: "Run: aws amplify list-apps, then: aws amplify get-app --app-id <app-id> --query 'app.environmentVariables'",
        }

    def configure_application(self, tf_output: dict) -> None:
        self.pretty_print_tf_output(tf_output)

    def pretty_print_tf_output(self, tf_output: dict) -> None:
        print("\n=== Amplify Env Vars Lab ===")
        print(f"  Access Key ID     : {tf_output.get('attacker_access_key_id', {}).get('value', 'N/A')}")
        print(f"  Secret Access Key : {tf_output.get('attacker_secret_access_key', {}).get('value', 'N/A')}")
        print(f"  Amplify App ID    : {tf_output.get('amplify_app_id', {}).get('value', 'N/A')}")
        print(f"  Amplify App Name  : {tf_output.get('amplify_app_name', {}).get('value', 'N/A')}")
        print("\nGoal: Retrieve the Amplify app definition and read the flag from environment variables.")
