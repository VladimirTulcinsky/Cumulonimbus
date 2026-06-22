from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1190", "name": "Exploit Public-Facing Application", "url": "https://attack.mitre.org/techniques/T1190/"},
        {"id": "T1580", "name": "Cloud Infrastructure Discovery", "url": "https://attack.mitre.org/techniques/T1580/"},
        {"id": "T1530", "name": "Data from Cloud Storage", "url": "https://attack.mitre.org/techniques/T1530/"},
    ]

    def get_flag(self) -> str:
        return "CUMULONIMBUS{L4mbd4_Funct10n_URL_N0_Auth}"
    def get_hints(self) -> dict:
        return {
            1: "Lambda Function URLs can be configured with no authentication, making them publicly accessible. Try calling the URL directly.",
            2: "Use `curl <function_url>` — a GET request is all that's needed. No AWS credentials required.",
            3: "The function returns a JSON response. Look at the `flag` key in the response body.",
        }

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  Function name : {output.get('function_name', {}).get('value', 'N/A')}")
        print(f"  Function URL  : {output.get('function_url', {}).get('value', 'N/A')}")
        print("\nGoal: Retrieve the flag by calling the public Lambda Function URL.")
        self.print_mitre_ttps()