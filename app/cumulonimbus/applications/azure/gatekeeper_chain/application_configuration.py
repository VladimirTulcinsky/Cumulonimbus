from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1098.003", "name": "Account Manipulation: Additional Cloud Roles", "url": "https://attack.mitre.org/techniques/T1098/003/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
        {"id": "T1552.001", "name": "Unsecured Credentials: Credentials in Files", "url": "https://attack.mitre.org/techniques/T1552/001/"},
        {"id": "T1580", "name": "Cloud Infrastructure Discovery", "url": "https://attack.mitre.org/techniques/T1580/"},
    ]

    def get_flag(self) -> str:
        return "CUMULONIMBUS{G4t3k33p3r_RBAC_Pr1v3sc_Ch41n}"

    def get_hints(self) -> dict:
        return {
            1: "You start with NO Azure access. Begin unauthenticated: read the public 'welcome.txt' blob (URL is in the lab output) to get your first flag and the gatekeeper's URL.",
            2: "Submit a flag to the gatekeeper to be GRANTED real Azure access: `curl -X POST <gatekeeper-url>/unlock -H 'Content-Type: application/json' -d '{\"flag\":\"<flag>\"}'`. Each correct flag adds a role to your account — wait 1-2 minutes for RBAC to propagate, then log in as the attacker.",
            3: "The ladder: flag0 -> Reader (read resource-group tags for flag1) -> App Configuration Data Reader (`az appconfig kv list --auth-mode login` for flag2) -> Storage Blob Data Reader (read the private 'vault-notes/notes.txt' for flag3) -> Key Vault Secrets User.",
            4: "After the final unlock, read the secret: `az keyvault secret show --vault-name <kv> --name app-flag --query value -o tsv`. That value is the flag.",
        }

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  Attacker UPN        : {output.get('attacker_upn', {}).get('value', 'N/A')}")
        print(f"  Attacker password   : {output.get('attacker_password', {}).get('value', 'N/A')}")
        print(f"  Resource group      : {output.get('resource_group_name', {}).get('value', 'N/A')}")
        print(f"  Gatekeeper URL      : {output.get('gatekeeper_url', {}).get('value', 'N/A')}")
        print(f"  Gatekeeper IP       : {output.get('gatekeeper_ip', {}).get('value', 'N/A')}")
        print(f"  Start here          : {output.get('start_here', {}).get('value', 'N/A')}")
        print("\nThis is a FLAG-GATED privilege-escalation ladder. You start with no")
        print("access. Find a flag, submit it to the gatekeeper, and it grants your")
        print("account the next Azure role for real:")
        print("  public blob (flag) -> Reader -> App Configuration -> Blob -> Key Vault")
        print("\nSubmit a flag:")
        print("  curl -s -X POST <gatekeeper-url>/unlock \\")
        print("       -H 'Content-Type: application/json' -d '{\"flag\":\"CUMULONIMBUS{...}\"}'")
        print("\nNOTE: the gatekeeper may take a few minutes on first boot (it installs")
        print("dependencies), and each granted role takes 1-2 minutes to propagate.")
        self.print_mitre_ttps()
