from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1552.001", "name": "Unsecured Credentials: Credentials in Files", "url": "https://attack.mitre.org/techniques/T1552/001/"},
        {"id": "T1580", "name": "Cloud Infrastructure Discovery", "url": "https://attack.mitre.org/techniques/T1580/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
    ]

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

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  Attacker UPN     : {output.get('attacker_upn', {}).get('value', 'N/A')}")
        print(f"  Attacker password: {output.get('attacker_password', {}).get('value', 'N/A')}")
        print(f"  VM name          : {output.get('vm_name', {}).get('value', 'N/A')}")
        print(f"  Resource group   : {output.get('resource_group_name', {}).get('value', 'N/A')}")
        print("\nLogin as the attacker:")
        print("  az login --username <upn> --password <password>")
        print("\nGoal: Read the VM extension settings to find the flag embedded in commandToExecute.")
        self.print_mitre_ttps()