# Amplify Env Vars — Secrets in App Environment Variables

**Provider**: AWS  
**Difficulty**: Beginner  
**MITRE ATT&CK**: [T1552.001 — Credentials in Files](https://attack.mitre.org/techniques/T1552/001/)

## Scenario

You have obtained AWS credentials for an IAM user with Amplify read access. A developer stored a secret flag directly in an AWS Amplify app's environment variables. The full app definition — including all environment variables — is returned by the `GetApp` API.

## Objective

Retrieve the Amplify app definition and read the flag from environment variables.

## Permissions

The attacker IAM user has the following permissions:

- `amplify:ListApps`
- `amplify:GetApp`
- `amplify:ListBranches`
- `amplify:GetBranch`

## Attack Path

1. Configure AWS CLI with the provided credentials.
2. List Amplify apps to find the target:
   ```bash
   aws amplify list-apps
   ```
3. Retrieve the full app definition including environment variables:
   ```bash
   aws amplify get-app --app-id <app-id> --query 'app.environmentVariables'
   ```
4. The `SECRET_FLAG` key contains the flag.

## Flag

`CUMULONIMBUS{4mpl1fy_App_3nv_V4rs_3xp0s3d}`

## Remediation

- Never store secrets directly in Amplify environment variables — they are returned in plaintext by `GetApp` to any principal with `amplify:GetApp`.
- Store secrets in AWS Secrets Manager or SSM Parameter Store (SecureString) and retrieve them at runtime using the application's execution role.
- Apply least-privilege IAM: restrict `amplify:GetApp` to specific app ARNs and limit who can call it.
- Audit existing Amplify apps: `aws amplify list-apps --query 'apps[].{name:name,envVars:environmentVariables}'` to check for exposed secrets.
