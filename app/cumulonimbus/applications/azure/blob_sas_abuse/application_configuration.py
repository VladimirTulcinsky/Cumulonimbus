from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract
import cumulonimbus.core.utils as utils
import os


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1552.001", "name": "Unsecured Credentials: Credentials in Files", "url": "https://attack.mitre.org/techniques/T1552/001/"},
        {"id": "T1619", "name": "Cloud Storage Object Discovery", "url": "https://attack.mitre.org/techniques/T1619/"},
        {"id": "T1530", "name": "Data from Cloud Storage", "url": "https://attack.mitre.org/techniques/T1530/"},
    ]
    def configure_application(self, **kwargs):
        pass

    def get_difficulty(self):
        return "Beginner"

    def get_hints(self):
        return {
            1: "Browse to the web app endpoint and view the page source. Developers sometimes leave credentials in JavaScript files — check app.js.",
            2: "app.js contains a SAS_TOKEN variable (a query string starting with '?sv='). With it you can enumerate all containers: curl 'https://<account>.blob.core.windows.net/?restype=account&comp=list&<sas>'. No SAS? Brute-force container names with gobuster, ffuf, cloudbrute, or BlobHunter using SecLists wordlists (e.g. SecLists/Discovery/Cloud/azure-storage-containers.txt).",
            3: "Use the SAS token to read the private 'secrets' container: curl 'https://<account>.blob.core.windows.net/secrets/flag.txt?<sas>'",
        }

    def get_flag(self):
        return "CUMULONIMBUS{SAS_T0k3n_N3v3r_1n_C0d3}"

    def pretty_print_tf_output(self, app_id, output):
        if not output:
            return
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] Web app endpoint  : " + output["web_endpoint"]["value"])
        print("[2] app.js URL        : " + output["app_js_url"]["value"])
        print("[3] Storage account   : " + output["storage_account_name"]["value"])
        print("")
        print("Start by browsing to the web endpoint and inspecting app.js.")
        self.print_mitre_ttps()