from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1098.003", "name": "Account Manipulation: Additional Cloud Roles", "url": "https://attack.mitre.org/techniques/T1098/003/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
        {"id": "T1552.001", "name": "Unsecured Credentials: Credentials in Files", "url": "https://attack.mitre.org/techniques/T1552/001/"},
        {"id": "T1580", "name": "Cloud Infrastructure Discovery", "url": "https://attack.mitre.org/techniques/T1580/"},
    ]

    def get_flag(self) -> str:
        return "CUMULONIMBUS{G4t3k33p3r_Ch41n_2_RBAC_Pr1v3sc}"

    def get_hints(self) -> dict:
        return {
            1: "You start with NO Azure access. Begin unauthenticated: read the public 'welcome.txt' blob (URL is in the lab output) to get your bootstrap flag, the resource group, and the gatekeeper's URL.",
            2: "Submit a flag to the gatekeeper to be GRANTED real Azure access (scoped to exactly the next resource): `curl -X POST <gatekeeper-url>/unlock -H 'Content-Type: application/json' -d '{\"flag\":\"<flag>\"}'`. Wait 1-2 minutes for RBAC to propagate, then read the resource. Each stage's value is the flag that unlocks the next.",
            3: "The ladder walks plaintext-credential scenarios in this order: resource-group tags (`az group show --query tags`) -> ARM deployment history (`az deployment group show --query properties.parameters`) -> policy assignment metadata (`az policy assignment show --query metadata`) -> Container App env (`az containerapp show`) -> Logic App (`az logic workflow show` / REST) -> Deployment Script outputs (`az deployment-scripts show`).",
            4: "App Service settings need Website Contributor (`az webapp config appsettings list`) — SECRET_FLAG is the flag and NEXT_HOP names the Key Vault. Submitting it grants Key Vault Secrets User: `az keyvault secret show --vault-name <kv> --name app-flag --query value -o tsv`.",
        }

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        gatekeeper_url = output.get('gatekeeper_url', {}).get('value', 'N/A')
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  Attacker UPN        : {output.get('attacker_upn', {}).get('value', 'N/A')}")
        print(f"  Attacker password   : {output.get('attacker_password', {}).get('value', 'N/A')}")
        print(f"  Resource group      : {output.get('resource_group_name', {}).get('value', 'N/A')}")
        print(f"  Gatekeeper URL      : {gatekeeper_url}")
        print(f"  Gatekeeper IP       : {output.get('gatekeeper_ip', {}).get('value', 'N/A')}")
        print(f"  Start here          : {output.get('start_here', {}).get('value', 'N/A')}")
        print("\nThis is a FLAG-GATED privilege-escalation ladder over the real")
        print("plaintext-credential scenarios. You start with no access. Find a flag,")
        print("submit it to the gatekeeper, and it grants your account the next Azure")
        print("role (scoped to one resource) for real:")
        print("  public blob -> resource-group tags -> ARM deployment history")
        print("  -> policy assignment -> Container App -> Logic App -> Deployment Script")
        print("  -> App Service -> Key Vault")
        print("\nSubmit a flag:")
        print(f"  curl -s -X POST {gatekeeper_url}/unlock \\")
        print("       -H 'Content-Type: application/json' -d '{\"flag\":\"CUMULONIMBUS{...}\"}'")
        print("\nNOTE: the gatekeeper takes a couple of minutes on first boot, and each")
        print("granted role takes 1-2 minutes to propagate.")
        self.print_mitre_ttps()
