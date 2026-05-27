from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1530", "name": "Data from Cloud Storage", "url": "https://attack.mitre.org/techniques/T1530/"},
        {"id": "T1580", "name": "Cloud Infrastructure Discovery", "url": "https://attack.mitre.org/techniques/T1580/"},
    ]

    def get_flag(self) -> str:
        return "CUMULONIMBUS{SQS_Publ1c_R3s0urc3_P0l1cy_R3c31v3}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "The SQS queue has a resource policy allowing any principal to receive messages. No IAM credentials are required — just the queue URL.",
            2: "Use `aws sqs receive-message --queue-url <url>` without configuring a profile. The queue URL is in the lab output.",
            3: "Run `aws sqs receive-message --queue-url <url> --region eu-west-1 --query 'Messages[0].Body' --output text` to read the flag from the message body.",
        }

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  Queue name : {output.get('queue_name', {}).get('value', 'N/A')}")
        print(f"  Queue URL  : {output.get('queue_url', {}).get('value', 'N/A')}")
        print("\nGoal: Receive messages from the publicly readable SQS queue without credentials.")
        self.print_mitre_ttps()