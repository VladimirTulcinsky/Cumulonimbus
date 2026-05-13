from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):

    def get_flag(self) -> str:
        return "CUMULONIMBUS{L4mbd4_Funct10n_URL_N0_Auth}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "Lambda Function URLs can be configured with no authentication, making them publicly accessible. Try calling the URL directly.",
            2: "Use `curl <function_url>` — a GET request is all that's needed. No AWS credentials required.",
            3: "The function returns a JSON response. Look at the `flag` key in the response body.",
        }

    def configure_application(self, tf_output: dict) -> None:
        self.pretty_print_tf_output(tf_output)

    def pretty_print_tf_output(self, tf_output: dict) -> None:
        print("\n=== Lambda Function URL Lab ===")
        print(f"  Function name : {tf_output.get('function_name', {}).get('value', 'N/A')}")
        print(f"  Function URL  : {tf_output.get('function_url', {}).get('value', 'N/A')}")
        print("\nGoal: Retrieve the flag by calling the public Lambda Function URL.")
