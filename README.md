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
