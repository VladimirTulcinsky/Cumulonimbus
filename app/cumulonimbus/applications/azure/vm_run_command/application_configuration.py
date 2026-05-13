from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):

    def get_flag(self) -> str:
        return "CUMULONIMBUS{VM_RunC0mm4nd_Arb1tr4ry_Exec}"

    def get_difficulty(self) -> str:
        return "Intermediate"

    def get_hints(self) -> dict:
        return {
            1: "Your attacker account has Virtual Machine Contributor on the resource group. This role includes the ability to execute commands on VMs without SSH access.",
            2: "Use `az vm run-command invoke --command-id RunShellScript` to execute arbitrary shell commands on the VM as root.",
            3: "Run `az vm run-command invoke --resource-group <rg> --name <vm> --command-id RunShellScript --scripts 'cat /root/flag.txt'` to read the flag.",
        }

    def configure_application(self, tf_output: dict) -> None:
        self.pretty_print_tf_output(tf_output)

    def pretty_print_tf_output(self, tf_output: dict) -> None:
        print("\n=== VM RunCommand Lab ===")
        print(f"  Attacker UPN     : {tf_output.get('attacker_upn', {}).get('value', 'N/A')}")
        print(f"  Attacker password: {tf_output.get('attacker_password', {}).get('value', 'N/A')}")
        print(f"  VM name          : {tf_output.get('vm_name', {}).get('value', 'N/A')}")
        print(f"  Resource group   : {tf_output.get('resource_group_name', {}).get('value', 'N/A')}")
        print("\nLogin as the attacker:")
        print("  az login --username <upn> --password <password>")
        print("\nGoal: Execute commands on the VM via RunCommand to read the flag.")
