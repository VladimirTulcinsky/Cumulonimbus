from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1552.001", "name": "Unsecured Credentials: Credentials in Files", "url": "https://attack.mitre.org/techniques/T1552/001/"},
        {"id": "T1580", "name": "Cloud Infrastructure Discovery", "url": "https://attack.mitre.org/techniques/T1580/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
    ]

    def get_flag(self) -> str:
        return "CUMULONIMBUS{3v3ntGr1d_W3bh00k_T0k3n_3xp0s3d}"

    def get_difficulty(self) -> str:
        return "Intermediate"

    def get_hints(self) -> dict:
        return {
            1: "Event Grid event subscriptions store their webhook URL in the subscription definition. Any Reader on the resource can retrieve it via ARM.",
            2: "Use `az eventgrid event-subscription list --source-resource-id <topic-id>` to find the subscription, then `az eventgrid event-subscription show` to get the full details.",
            3: "The webhook URL contains a `token` query parameter with the flag. Extract it with `--query \"destination.endpointUrl\"`.",
        }

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  Attacker UPN     : {output.get('attacker_upn', {}).get('value', 'N/A')}")
        print(f"  Attacker password: {output.get('attacker_password', {}).get('value', 'N/A')}")
        print(f"  Topic name       : {output.get('topic_name', {}).get('value', 'N/A')}")
        print(f"  Resource group   : {output.get('resource_group_name', {}).get('value', 'N/A')}")
        print("\nLogin as the attacker:")
        print("  az login --username <upn> --password <password>")
        print("\nGoal: Extract the flag from the Event Grid webhook URL token parameter.")
        self.print_mitre_ttps()