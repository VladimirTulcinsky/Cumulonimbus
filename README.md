# Cumulonimbus: A Vulnerable Cloud Environment

> **Warning:** This cyber range deploys intentionally vulnerable infrastructure.
> Do **not** use it in production or in an environment with sensitive data.

## Available Labs

| App ID | Provider | Category | Difficulty |
|--------|----------|----------|------------|
| `ec2_ssrf` | AWS | SSRF / IMDS | Beginner |
| `sa_public_access` | Azure | Storage Misconfiguration | Beginner |
| `cloudshell` | Azure | Storage / RBAC | Intermediate |
| `illicit_consent_grant` | Azure | Identity / OAuth Phishing | Intermediate |
| `managed_identity_abuse` | Azure | Compute / IMDS | Intermediate |
| `add_sp_credentials` | Azure | Identity / Privilege Escalation | Advanced |
| `foci` | Azure | Identity / OAuth Token Abuse | Advanced |
| `shared_key_auth` | Azure | Storage / Function App / Key Vault | Advanced |
| `blob_sas_abuse` | Azure | Storage / Credential Exposure | Beginner |
| `keyvault_misconfig` | Azure | Key Vault / Access Policy | Intermediate |
| `automation_account` | Azure | Automation / Managed Identity | Intermediate |
| `function_ssrf` | Azure | Serverless / SSRF / IMDS | Intermediate |
| `s3_public_access` | AWS | Storage / Misconfiguration | Beginner |
| `lambda_env_secrets` | AWS | Serverless / Credential Exposure | Beginner |
| `ec2_userdata_secrets` | AWS | Compute / Credential Exposure | Beginner |
| `secrets_manager_enum` | AWS | IAM / Secrets Management | Intermediate |
| `ssm_parameter_store` | AWS | IAM / Secrets Management | Intermediate |
| `iam_privesc` | AWS | IAM / Privilege Escalation | Advanced |
| `terraform_state_exposure` | Azure | Storage / Secrets in State | Intermediate |
| `arm_deployment_history` | Azure | ARM / Credential Exposure | Intermediate |
| `exposed_app_registration` | Azure | Identity / Credential Exposure | Intermediate |
| `s3_bucket_versioning` | AWS | Storage / Versioning | Beginner |
| `cloudformation_stack` | AWS | Infrastructure / Secrets | Beginner |
| `sts_assume_role_any` | AWS | IAM / Privilege Escalation | Intermediate |
| `app_service_env_vars` | Azure | Web / Secrets | Beginner |
| `lambda_function_url` | AWS | Serverless / Exposure | Beginner |
| `cognito_identity_pool` | AWS | Identity / Credential Abuse | Intermediate |
| `logic_app_credentials` | Azure | Integration / Secrets | Intermediate |
| `storage_account_keys` | Azure | Storage / Privilege Escalation | Intermediate |
| `s3_object_public_acl` | AWS | Storage / Misconfiguration | Beginner |
| `glue_job_secrets` | AWS | Data / Secrets | Beginner |
| `vm_run_command` | Azure | Compute / Privilege Escalation | Intermediate |
| `container_instance_env` | Azure | Containers / Secrets | Beginner |
| `sqs_public_receive` | AWS | Messaging / Misconfiguration | Beginner |
| `ssm_session_manager` | AWS | Compute / Lateral Movement | Intermediate |
| `resource_group_tags` | Azure | Identity / Secrets | Beginner |
| `eventgrid_webhook_token` | Azure | Integration / Secrets | Intermediate |
| `codebuild_env_vars` | AWS | CI/CD / Secrets | Beginner |
| `stepfunctions_execution_history` | AWS | Serverless / Data Exposure | Intermediate |
| `app_configuration_secrets` | Azure | Configuration / Secrets | Beginner |
| `vm_extension_settings` | Azure | Compute / Secrets | Beginner |

## Quick Start

The easiest way to run Cumulonimbus is via the Docker container, which bundles all
dependencies (Terraform, AWS CLI, Azure CLI).

```shell
docker run -it cumulonimbuscloud/cumulonimbus:latest
```

Or build locally:

```shell
docker build -t cumulonimbus .
docker run -it cumulonimbus
```

---

## Prerequisites

You need a cloud account with sufficient permissions before deploying labs.

**Azure** — create a service principal with:
- Global Administrator role (Entra ID level)
- Owner on the target subscription
- Key Vault Administrator on the target subscription
- Security defaults disabled

**AWS** — an IAM user or role with:
- `AdministratorAccess` (or at minimum EC2, S3, and IAM full access)

---

## CLI Reference

### Authenticate

```shell
# Azure
./cnimbus.py azure authenticate --service-principal \
  --client-id <id> --client-secret <secret> \
  --tenant-id <tenant> --subscription-id <subscription>

# AWS
./cnimbus.py aws authenticate \
  --access-key-id <key-id> --secret-access-key <secret> \
  [--session-token <token>]
```

### Deploy a lab

```shell
./cnimbus.py azure create --app-id <app-id>
./cnimbus.py aws   create --app-id <app-id>
```

### Destroy a lab

```shell
./cnimbus.py azure destroy --app-id <app-id>
./cnimbus.py aws   destroy --app-id <app-id>
```

### Validate a captured flag

```shell
./cnimbus.py azure validate --app-id <app-id> --flag "CUMULONIMBUS{...}"
./cnimbus.py aws   validate --app-id <app-id> --flag "Cumulonimbus{...}"
```

### Get a hint

```shell
# Level 1 = gentle nudge, 2 = moderate, 3 = explicit
./cnimbus.py azure hint --app-id <app-id> --level 1
./cnimbus.py aws   hint --app-id <app-id> --level 2
```

---

## CTFd Integration

A self-hosted CTFd instance can be used to score flag submissions across teams.
See [`ctfd/README.md`](ctfd/README.md) for setup instructions.

```shell
cd ctfd
docker compose up -d
python seed_challenges.py --url http://localhost:8000 --admin-token <token>
```

---

## For more help

```shell
./cnimbus.py -h
./cnimbus.py azure -h
./cnimbus.py aws -h
```
