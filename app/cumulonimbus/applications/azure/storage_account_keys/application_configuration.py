from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
        {"id": "T1552", "name": "Unsecured Credentials", "url": "https://attack.mitre.org/techniques/T1552/"},
        {"id": "T1530", "name": "Data from Cloud Storage", "url": "https://attack.mitre.org/techniques/T1530/"},
        {"id": "T1548", "name": "Privilege Escalation", "url": "https://attack.mitre.org/techniques/T1548/"},
    ]

    def get_flag(self) -> str:
        return "CUMULONIMBUS{St0r4g3_Acc0unt_K3ys_Byp4ss_RBAC}"

    def get_difficulty(self) -> str:
        return "Intermediate"

    def get_hints(self) -> dict:
        return {
            1: "Your attacker account has Storage Account Contributor on the storage account. This is a control-plane role — check what actions it includes beyond just metadata management.",
            2: "`Storage Account Contributor` includes `Microsoft.Storage/storageAccounts/listKeys/action`. Use `az storage account keys list` to retrieve the account keys.",
            3: "Use the account key with `az storage blob download --account-key <key>` to access the private `internal-secrets` container and download `credentials.txt`.",
        }

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("\n=== Storage Account Keys — RBAC Bypass Lab ===")
        print(f"  Attacker UPN      : {output.get('attacker_upn', {}).get('value', 'N/A')}")
        print(f"  Attacker password : {output.get('attacker_password', {}).get('value', 'N/A')}")
        print(f"  Storage account   : {output.get('storage_account_name', {}).get('value', 'N/A')}")
        print(f"  Resource group    : {output.get('resource_group_name', {}).get('value', 'N/A')}")
        print(f"  Container         : {output.get('container_name', {}).get('value', 'N/A')}")
        print("\nLogin as the attacker:")
        print("  az login --username <upn> --password <password>")
        print("\nGoal: Use the Storage Account Contributor role to bypass data-plane RBAC and read the flag.")
        print("\nNOTE: Complete this challenge via CLI only.")
        print("  The Azure portal now silently uses storage account keys when the signed-in user has")
        print("  listKeys permission, so blobs appear readable in the portal without any exploitation.")
        print("  Follow the CLI steps in the README to understand the actual attack technique.")
        self.print_mitre_ttps()