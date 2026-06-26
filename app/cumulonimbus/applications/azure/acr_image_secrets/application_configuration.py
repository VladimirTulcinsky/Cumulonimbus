from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1552.001", "name": "Unsecured Credentials: Credentials in Files", "url": "https://attack.mitre.org/techniques/T1552/001/"},
        {"id": "T1525", "name": "Implant Internal Image", "url": "https://attack.mitre.org/techniques/T1525/"},
        {"id": "T1613", "name": "Container and Resource Discovery", "url": "https://attack.mitre.org/techniques/T1613/"},
    ]

    def get_flag(self) -> str:
        return "CUMULONIMBUS{4CR_Adm1n_Cr3ds_2_D3l3t3d_L4y3r_S3cr3t}"

    def get_hints(self) -> dict:
        return {
            1: "The resource group holds a private Azure Container Registry. You only have Reader, so you cannot list the registry's credentials directly — but someone may have left them somewhere a Reader can read. Inspect resource tags.",
            2: "The storage account's tags leak the registry admin username and password (`az resource show --ids <sa-id>` or `az tag list`). This container has no Docker, so authenticate with `crane` (pre-installed): `crane auth login <login-server> -u <user> -p <password>`, then inspect `<login-server>/cumulonimbus/app:latest`.",
            3: "The flattened filesystem has /app/config/app.config with an OLD rotated token (a decoy): `crane export <img> - | grep -ao 'CUMULONIMBUS{[^}]*}'`. The real secret was written into a layer and 'deleted' later — recover it from the image history: `crane config <img> | grep -ao 'CUMULONIMBUS{[^}]*}'`. The flag is the DEPLOY_TOKEN value. (Docker works too if you have it: `docker history --no-trunc` / `docker save`.)",
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
        print(f"  Registry login server: {output.get('acr_login_server', {}).get('value', 'N/A')}")
        print(f"  Leaky storage account: {output.get('leak_storage_account', {}).get('value', 'N/A')}")
        print(f"  Image reference     : {output.get('image_reference', {}).get('value', 'N/A')}")
        print("\nLogin as the attacker (Reader on the resource group):")
        print("  az login --username <upn> --password <password>")
        print("\nGoal: the registry's admin credentials are leaked in a resource's tags.")
        print("Use them to pull the image, then dig the secret out of it — the obvious")
        print("runtime config is a decoy; the real flag hides in a deleted image layer.")
        self.print_mitre_ttps()
