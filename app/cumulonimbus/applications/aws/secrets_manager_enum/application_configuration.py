from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def configure_application(self, **kwargs):
        pass

    def get_difficulty(self):
        return "Intermediate"

    def get_hints(self):
        return {
            1: "Use your credentials to list all secrets: aws secretsmanager list-secrets --profile attacker. Notice the policy uses a wildcard resource path.",
            2: "Filter for secrets under the /cumulonimbus/ prefix. Each one can be read with: aws secretsmanager get-secret-value --secret-id <arn_or_name>",
            3: "Iterate over all listed secret ARNs and dump their values. The flag is in the secret named /cumulonimbus/production/flag-<id>.",
        }

    def get_flag(self):
        return "CUMULONIMBUS{S3cr3ts_M4n4g3r_0v3rp3rm1ss1v3}"

    def pretty_print_tf_output(self, app_id, output):
        if not output:
            return
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] aws_access_key_id     : " + output["attacker_aws_access_key_id"]["value"])
        print("[2] aws_secret_access_key : " + output["attacker_aws_secret_access_key"]["value"])
        print("[3] secret_prefix         : " + output["secret_prefix"]["value"])
        print("")
        print("Configure the attacker profile and enumerate secrets:")
        print("  aws configure --profile attacker  # region: eu-west-1")
        print("  aws secretsmanager list-secrets --profile attacker")
