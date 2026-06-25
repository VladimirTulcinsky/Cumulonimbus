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
            1: "You start with NO Azure access. Begin unauthenticated: read the public 'welcome.txt' blob (URL is in the lab output) to get your bootstrap flag, the resource group, and the gatekeeper's URL.",
            2: "Submit a flag to the gatekeeper to be GRANTED real Azure access (scoped to exactly the next resource): `curl -X POST <gatekeeper-url>/unlock -H 'Content-Type: application/json' -d '{\"flag\":\"<flag>\"}'`. Wait 1-2 minutes for RBAC to propagate, then read the resource. Each stage's value is the flag that unlocks the next.",
            3: "The ladder walks the real plaintext-credential scenarios in this order: ACR image (pull from the registry and dig the secret out of an image layer) -> Container Instance env (`az container show`) -> Data Factory linked service (`az datafactory linked-service show`) -> App Configuration (`az appconfig kv list --auth-mode login`) -> Monitor action group (`az monitor action-group show`) -> APIM named value (`az apim nv show ... --named-value-id flag-key`).",
            4: "For the ACR stage there is no Docker in this container — use `crane` (pre-installed): `TOKEN=$(az acr login -n <acr> --expose-token --query accessToken -o tsv)`, `crane auth login <acr>.azurecr.io -u 00000000-0000-0000-0000-000000000000 -p $TOKEN`. The real flag is in the image history (`crane config <img> | grep -ao 'CUMULONIMBUS{[^}]*}'`); the runtime file is a decoy. The final unlock grants Key Vault Secrets User: `az keyvault secret show --vault-name <kv> --name app-flag --query value -o tsv` (the vault name/secret are in the APIM `next-hop` named value).",
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
        print("  public blob -> ACR image -> Container Instance -> Data Factory")
        print("  -> App Configuration -> Monitor action group -> APIM -> Key Vault")
        print("\nSubmit a flag:")
        print(f"  curl -s -X POST {gatekeeper_url}/unlock \\")
        print("       -H 'Content-Type: application/json' -d '{\"flag\":\"CUMULONIMBUS{...}\"}'")
        print("\nNOTE: the gatekeeper takes a couple of minutes on first boot, and each")
        print("granted role takes 1-2 minutes to propagate.")
        self.print_mitre_ttps()
