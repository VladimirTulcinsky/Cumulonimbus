from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):

    def get_flag(self) -> str:
        return "CUMULONIMBUS{C0d3Bu1ld_Pl41nt3xt_Env_V4rs}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "AWS CodeBuild stores environment variables in the project definition. PLAINTEXT type variables are returned unmasked by codebuild:BatchGetProjects.",
            2: "Use `aws codebuild list-projects` to find the project name, then `aws codebuild batch-get-projects --names <name>`.",
            3: "Look for the `DEPLOY_API_KEY` entry in `projects[0].environment.environmentVariables` — its value contains the flag.",
        }

    def configure_application(self, tf_output: dict) -> None:
        self.pretty_print_tf_output(tf_output)

    def pretty_print_tf_output(self, tf_output: dict) -> None:
        print("\n=== CodeBuild Environment Variables Lab ===")
        print(f"  Attacker user     : {tf_output.get('attacker_username', {}).get('value', 'N/A')}")
        print(f"  Access key ID     : {tf_output.get('attacker_access_key_id', {}).get('value', 'N/A')}")
        print(f"  Secret access key : {tf_output.get('attacker_secret_access_key', {}).get('value', 'N/A')}")
        print(f"  Project name      : {tf_output.get('project_name', {}).get('value', 'N/A')}")
        print("\nConfigure the attacker profile:")
        print("  aws configure --profile attacker   # region: eu-west-1")
        print("\nGoal: Retrieve the flag from the CodeBuild project's plaintext environment variables.")
