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

    def configure_application(self, tf_output: dict) -> None:
        self.pretty_print_tf_output(tf_output)

    def pretty_print_tf_output(self, tf_output: dict) -> None:
        print("\n=== ECS Exec Lab ===")
        print(f"  Access Key ID     : {tf_output.get('attacker_access_key_id', {}).get('value', 'N/A')}")
        print(f"  Secret Access Key : {tf_output.get('attacker_secret_access_key', {}).get('value', 'N/A')}")
        print(f"  Cluster Name      : {tf_output.get('cluster_name', {}).get('value', 'N/A')}")
        print(f"  Service Name      : {tf_output.get('service_name', {}).get('value', 'N/A')}")
        print("\nGoal: Use ECS Exec to open an interactive shell inside the running container and read the flag.")
