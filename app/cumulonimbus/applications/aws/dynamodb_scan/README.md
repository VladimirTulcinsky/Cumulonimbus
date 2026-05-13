# DynamoDB Scan — Sensitive Data in Table Items

**Provider**: AWS  
**Difficulty**: Beginner  
**MITRE ATT&CK**: [T1530 — Data from Cloud Storage Object](https://attack.mitre.org/techniques/T1530/)

## Scenario

You have obtained AWS credentials for an IAM user with DynamoDB read access. A developer stored a sensitive API key directly as a DynamoDB table item alongside other configuration records. Scanning the table reveals the flag.

## Objective

Scan the DynamoDB table and retrieve the flag stored in a table item.

## Permissions

The attacker IAM user has the following permissions:

- `dynamodb:ListTables`
- `dynamodb:DescribeTable`
- `dynamodb:Scan`
- `dynamodb:GetItem`
- `dynamodb:Query`

## Attack Path

1. Configure AWS CLI with the provided credentials.
2. List DynamoDB tables:
   ```bash
   aws dynamodb list-tables
   ```
3. Scan all items in the table:
   ```bash
   aws dynamodb scan --table-name <table-name>
   ```
4. Inspect the items returned — the `value` field of the `flag` record contains the flag.

## Flag

`CUMULONIMBUS{Dyn4m0DB_Sc4n_D4t4_3xp0sur3}`

## Remediation

- Never store secrets, tokens, or credentials as DynamoDB table items — use AWS Secrets Manager or SSM Parameter Store (SecureString) instead.
- Apply fine-grained DynamoDB IAM conditions to restrict which tables and even which items a principal can access (`dynamodb:LeadingKeys` condition).
- Enable DynamoDB encryption at rest using customer-managed KMS keys.
- Use CloudTrail to audit `dynamodb:Scan` calls on sensitive tables and alert on unexpected access patterns.
