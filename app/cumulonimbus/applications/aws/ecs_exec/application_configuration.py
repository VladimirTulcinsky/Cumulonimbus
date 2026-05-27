from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def get_flag(self) -> str:
        return "CUMULONIMBUS{ECS_3x3c_C0nt41n3r_Sh3ll}"

    def get_difficulty(self) -> str:
        return "Intermediate"

    def get_hints(self) -> dict:
        return {
            1: "The IAM user has permissions related to ECS. Check what clusters and tasks are running.",
            2: "ECS Exec allows running interactive commands inside a running Fargate container. Look for the feature flag on the service.",
            3: "Run: aws ecs list-tasks --cluster <cluster-name>, then: aws ecs execute-command --cluster <cluster> --task <task-id> --container app --interactive --command 'cat /flag.txt'",
        }

    mitre_ttps = [
        {"id": "T1609", "name": "Container Administration Command", "url": "https://attack.mitre.org/techniques/T1609/"},
        {"id": "T1552.005", "name": "Unsecured Credentials: Cloud Instance Metadata API", "url": "https://attack.mitre.org/techniques/T1552/005/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
    ]

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("\n=== ECS Exec Lab ===")
        print(f"  Access Key ID     : {output.get('attacker_access_key_id', {}).get('value', 'N/A')}")
        print(f"  Secret Access Key : {output.get('attacker_secret_access_key', {}).get('value', 'N/A')}")
        print(f"  Cluster Name      : {output.get('cluster_name', {}).get('value', 'N/A')}")
        print(f"  Service Name      : {output.get('service_name', {}).get('value', 'N/A')}")
        print("\nGoal: Use ECS Exec to open an interactive shell inside the running container and read the flag.")
        self.print_mitre_ttps()
