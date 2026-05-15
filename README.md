<div align="center">

<img src="docs/logo.svg" alt="Cumulonimbus" width="860"/>

---

> ⚠️ **Warning:** This cyber range deploys intentionally vulnerable infrastructure.
> Do **not** use it in production or in an environment with sensitive data.

> 💸 **Cost notice:** Deploying a lab provisions **real cloud infrastructure** on your AWS or Azure account.
> Charges will be incurred. Always destroy labs when you are done:
> `cnimbus <provider> destroy --app-id <app-id>`

</div>

---

## Available Labs

<details>
<summary><strong>🔵 Azure Labs — 29 challenges</strong></summary>

<br>

**Beginner**

| App ID | Category |
|--------|----------|
| `sa_public_access` | Storage Misconfiguration |
| `blob_sas_abuse` | Storage / Credential Exposure |
| `app_service_env_vars` | Web / Secrets |
| `container_instance_env` | Containers / Secrets |
| `container_app_env_vars` | Containers / Secrets |
| `resource_group_tags` | Identity / Secrets |
| `app_configuration_secrets` | Configuration / Secrets |
| `vm_extension_settings` | Compute / Secrets |
| `apim_named_value` | API Management / Secrets |
| `deployment_script` | IaC / Data Exposure |
| `policy_assignment_metadata` | Governance / Secrets |
| `monitor_action_group` | Monitoring / Secrets |

**Intermediate**

| App ID | Category |
|--------|----------|
| `cloudshell` | Storage / RBAC |
| `illicit_consent_grant` | Identity / OAuth Phishing |
| `managed_identity_abuse` | Compute / IMDS |
| `keyvault_misconfig` | Key Vault / Access Policy |
| `automation_account` | Automation / Managed Identity |
| `function_ssrf` | Serverless / SSRF / IMDS |
| `terraform_state_exposure` | Storage / Secrets in State |
| `arm_deployment_history` | ARM / Credential Exposure |
| `exposed_app_registration` | Identity / Credential Exposure |
| `storage_account_keys` | Storage / Privilege Escalation |
| `vm_run_command` | Compute / Privilege Escalation |
| `eventgrid_webhook_token` | Integration / Secrets |
| `logic_app_credentials` | Integration / Secrets |
| `data_factory_linked_service` | Integration / Secrets |

**Advanced**

| App ID | Category |
|--------|----------|
| `add_sp_credentials` | Identity / Privilege Escalation |
| `foci` | Identity / OAuth Token Abuse |
| `shared_key_auth` | Storage / Function App / Key Vault |

</details>

<details>
<summary><strong>🟠 AWS Labs — 24 challenges</strong></summary>

<br>

**Beginner**

| App ID | Category |
|--------|----------|
| `ec2_ssrf` | SSRF / IMDS |
| `s3_public_access` | Storage / Misconfiguration |
| `s3_object_public_acl` | Storage / Misconfiguration |
| `s3_bucket_versioning` | Storage / Versioning |
| `lambda_env_secrets` | Serverless / Credential Exposure |
| `lambda_function_url` | Serverless / Exposure |
| `ec2_userdata_secrets` | Compute / Credential Exposure |
| `cloudformation_stack` | Infrastructure / Secrets |
| `glue_job_secrets` | Data / Secrets |
| `sqs_public_receive` | Messaging / Misconfiguration |
| `codebuild_env_vars` | CI/CD / Secrets |
| `route53_records` | DNS / Data Exposure |
| `dynamodb_scan` | Database / Data Exposure |
| `amplify_env_vars` | Frontend / Secrets |
| `appconfig_deployment` | Configuration / Secrets |

**Intermediate**

| App ID | Category |
|--------|----------|
| `secrets_manager_enum` | IAM / Secrets Management |
| `ssm_parameter_store` | IAM / Secrets Management |
| `sts_assume_role_any` | IAM / Privilege Escalation |
| `cognito_identity_pool` | Identity / Credential Abuse |
| `ssm_session_manager` | Compute / Lateral Movement |
| `ecs_exec` | Containers / Lateral Movement |
| `kinesis_shard_reader` | Streaming / Data Exposure |
| `stepfunctions_execution_history` | Serverless / Data Exposure |

**Advanced**

| App ID | Category |
|--------|----------|
| `iam_privesc` | IAM / Privilege Escalation |

</details>

---

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
- Microsoft Graph application permissions (admin consented): `User.ReadWrite.All`, `Application.ReadWrite.All`, `Directory.ReadWrite.All`

> Grant Graph permissions: Azure Portal → App registrations → your app → API permissions → Add a permission → Microsoft Graph → Application permissions → select the permissions above → Grant admin consent

**AWS** — an IAM user or role with:
- `AdministratorAccess` (or at minimum EC2, S3, and IAM full access)

---

## CLI Reference

### Authenticate

```shell
# Azure
cnimbus azure authenticate --service-principal \
  --client-id <id> --client-secret <secret> \
  --tenant-id <tenant> --subscription-id <subscription> \
  --tenant-domain <domain>          # e.g. contoso.onmicrosoft.com

# AWS
cnimbus aws authenticate \
  --access-key-id <key-id> --secret-access-key <secret> \
  [--session-token <token>]
```

### Deploy a lab

```shell
cnimbus azure create --app-id <app-id>
cnimbus aws   create --app-id <app-id>
```

### Destroy a lab

```shell
cnimbus azure destroy --app-id <app-id>
cnimbus aws   destroy --app-id <app-id>
```

### Validate a captured flag

```shell
cnimbus azure validate --app-id <app-id> --flag "CUMULONIMBUS{...}"
cnimbus aws   validate --app-id <app-id> --flag "Cumulonimbus{...}"
```

### Get a hint

```shell
# Level 1 = gentle nudge, 2 = moderate, 3 = explicit
cnimbus azure hint --app-id <app-id> --level 1
cnimbus aws   hint --app-id <app-id> --level 2
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
cnimbus -h
cnimbus azure -h
cnimbus aws -h
```
