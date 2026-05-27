from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def get_flag(self) -> str:
        return "CUMULONIMBUS{Monit0r_W3bh00k_T0k3n_3xp0s3d}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "Azure Monitor Action Groups define who gets notified when an alert fires. Webhook receivers store the full callback URL including any embedded tokens.",
            2: "Action Group definitions are part of ARM and readable by anyone with Reader on the resource group.",
            3: "Run: az monitor action-group list --resource-group <rg>, then: az monitor action-group show --name <name> --resource-group <rg> --query 'webhookReceivers'",
        }

    mitre_ttps = [
        {"id": "T1552", "name": "Unsecured Credentials", "url": "https://attack.mitre.org/techniques/T1552/"},
        {"id": "T1083", "name": "File and Directory Discovery", "url": "https://attack.mitre.org/techniques/T1083/"},
    ]

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("\n=== Monitor Action Group Lab ===")
        print(f"  Attacker Client ID     : {output.get('attacker_client_id', {}).get('value', 'N/A')}")
        print(f"  Attacker Client Secret : {output.get('attacker_client_secret', {}).get('value', 'N/A')}")
        print(f"  Resource Group         : {output.get('resource_group_name', {}).get('value', 'N/A')}")
        print(f"  Action Group Name      : {output.get('action_group_name', {}).get('value', 'N/A')}")
        print("\nGoal: Inspect the Action Group webhook receiver URL to find the embedded authentication token.")
        self.print_mitre_ttps()
