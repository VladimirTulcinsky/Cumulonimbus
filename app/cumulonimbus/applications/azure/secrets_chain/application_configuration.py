from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1552.001", "name": "Unsecured Credentials: Credentials in Files", "url": "https://attack.mitre.org/techniques/T1552/001/"},
        {"id": "T1528", "name": "Steal Application Access Token", "url": "https://attack.mitre.org/techniques/T1528/"},
        {"id": "T1580", "name": "Cloud Infrastructure Discovery", "url": "https://attack.mitre.org/techniques/T1580/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
    ]

    def get_flag(self) -> str:
        return "CUMULONIMBUS{Pl41nt3xt_Cr3d_Ch41n_2_K3yV4ult}"

    def get_hints(self) -> dict:
        return {
            1: "Start unauthenticated at the portal website. View its app.js — a SAS token is hardcoded in the client-side JavaScript (read+list over the whole storage account).",
            2: "Use the SAS token to list the account's containers and read the private 'onboarding' blob — it leaks a service principal's client id/secret/tenant. Log in: `az login --service-principal -u <id> -p <secret> --tenant <tenant>`.",
            3: "As the service principal (Reader on the resource group), read the resource group's tags (`az group show`) — a tag names the App Configuration store. Then `az appconfig kv list` (you have Data Reader) to find the Data Factory name.",
            4: "Read the Data Factory's linked services (`az datafactory linked-service show`) — the connection string embeds a storage account key in cleartext. Use it (`az storage blob download --account-key ...`) to read the private 'runtime' blob, which names the Container Instance.",
            5: "`az container show` exposes the container's environment variables, which give the Key Vault name and secret name. The service principal has Key Vault Secrets User, so `az keyvault secret show --vault-name <kv> --name app-flag` returns the flag.",
        }

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  Resource group      : {output.get('resource_group_name', {}).get('value', 'N/A')}")
        print(f"  Portal website acct : {output.get('portal_website_account', {}).get('value', 'N/A')}")
        print(f"  Portal website URL  : {output.get('portal_website_url', {}).get('value', 'N/A')}")
        print("\nThis is a SEQUENTIAL chain — each step's leaked value unlocks the next:")
        print("  1. Portal app.js leaks a SAS token")
        print("  2. SAS -> private blob leaks a service principal's credentials")
        print("  3. SP + resource-group tag -> App Configuration store")
        print("  4. App Configuration -> Data Factory -> linked-service storage key")
        print("  5. Storage key -> private blob -> Container Instance env vars")
        print("  6. Container env -> Key Vault name + secret -> the flag")
        print("\nStart by browsing the portal website and reading its app.js. No")
        print("credentials are needed for the first step.")
        self.print_mitre_ttps()
