from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):

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

    def configure_application(self, tf_output: dict) -> None:
        self.pretty_print_tf_output(tf_output)

    def pretty_print_tf_output(self, tf_output: dict) -> None:
        print("\n=== Storage Account Keys — RBAC Bypass Lab ===")
        print(f"  Attacker UPN      : {tf_output.get('attacker_upn', {}).get('value', 'N/A')}")
        print(f"  Attacker password : {tf_output.get('attacker_password', {}).get('value', 'N/A')}")
        print(f"  Storage account   : {tf_output.get('storage_account_name', {}).get('value', 'N/A')}")
        print(f"  Resource group    : {tf_output.get('resource_group_name', {}).get('value', 'N/A')}")
        print(f"  Container         : {tf_output.get('container_name', {}).get('value', 'N/A')}")
        print("\nLogin as the attacker:")
        print("  az login --username <upn> --password <password>")
        print("\nGoal: Use the Storage Account Contributor role to bypass data-plane RBAC and read the flag.")
