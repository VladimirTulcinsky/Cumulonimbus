from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):

    def get_flag(self) -> str:
        return "CUMULONIMBUS{VM_3xt3ns10n_S3tt1ngs_Pl41nt3xt}"

    def get_difficulty(self) -> str:
        return "Beginner"

    def get_hints(self) -> dict:
        return {
            1: "Azure VM extensions store their `settings` block as plaintext JSON in ARM. Any Reader can retrieve it — unlike `protectedSettings`, which are encrypted.",
            2: "Use `az vm extension list --vm-name <vm> --resource-group <rg>` to find the installed extension, then `az vm extension show` to read its settings.",
            3: "Run `az vm extension show --vm-name <vm> --resource-group <rg> --name configure-app --query settings` — the `commandToExecute` field contains the flag.",
        }

    def configure_application(self, tf_output: dict) -> None:
        self.pretty_print_tf_output(tf_output)

    def pretty_print_tf_output(self, tf_output: dict) -> None:
        print("\n=== VM Extension Settings Lab ===")
        print(f"  Attacker UPN     : {tf_output.get('attacker_upn', {}).get('value', 'N/A')}")
        print(f"  Attacker password: {tf_output.get('attacker_password', {}).get('value', 'N/A')}")
        print(f"  VM name          : {tf_output.get('vm_name', {}).get('value', 'N/A')}")
        print(f"  Resource group   : {tf_output.get('resource_group_name', {}).get('value', 'N/A')}")
        print("\nLogin as the attacker:")
        print("  az login --username <upn> --password <password>")
        print("\nGoal: Read the VM extension settings to find the flag embedded in commandToExecute.")
