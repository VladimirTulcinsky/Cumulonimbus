# CTFd for Cumulonimbus

Two independent CTFd instances — one per cloud provider — so challenges stay
focused and the AWS / Azure split is clear.

| Instance | URL                   | Challenges |
|----------|-----------------------|------------|
| AWS      | http://localhost:8000 | AWS labs   |
| Azure    | http://localhost:8001 | Azure labs |

## Quick Start

```bash
# 1. Start both instances
docker compose up -d

# 2. Initialise and seed each one
python setup.py --provider aws
python setup.py --provider azure
```

Each command waits for its CTFd instance to become ready, completes the setup
wizard, generates an admin API token, and seeds the matching challenges.

Default credentials for both instances: `admin` / `cumulonimbus`.

## Custom credentials / event name

```bash
python setup.py --provider aws \
  --ctf-name "Cloud CTF — AWS" \
  --admin-password supersecret

python setup.py --provider azure \
  --ctf-name "Cloud CTF — Azure" \
  --admin-password supersecret
```

## CTFd is already configured (existing install)

If you set up CTFd manually, pass your existing admin password:

```bash
python setup.py --provider aws   --admin-password <your_password>
python setup.py --provider azure --admin-password <your_password>
```

You will see this error if the flag is omitted and the default password is wrong:

```
ERROR: CTFd is already set up. Provide your admin password:
    python setup.py --provider <aws|azure> --admin-password <your_password>
```

## Manual seeding only (skip setup, use an existing token)

```bash
# AWS
python seed_challenges.py --provider aws \
  --url http://localhost:8000 --admin-token <token>

# Azure
python seed_challenges.py --provider azure \
  --url http://localhost:8001 --admin-token <token>
```

## Running a single instance

```bash
# AWS only
docker compose up -d ctfd_aws db_aws cache_aws

# Azure only
docker compose up -d ctfd_azure db_azure cache_azure
```

## Teardown

```bash
# Both instances (removes all data)
docker compose down -v

# One instance only
docker compose down ctfd_aws db_aws cache_aws
docker volume rm ctfd_ctfd_aws_db ctfd_ctfd_aws_logs ctfd_ctfd_aws_uploads ctfd_ctfd_aws_cache
```

## Environment Variables

| Variable                | Default                | Description                              |
|-------------------------|------------------------|------------------------------------------|
| `CTFD_AWS_SECRET_KEY`   | `change-me-aws`        | Flask secret key for the AWS instance    |
| `CTFD_AZURE_SECRET_KEY` | `change-me-azure`      | Flask secret key for the Azure instance  |

## Workflow with Cumulonimbus

1. Deploy a lab: `cnimbus aws create --app-id ec2_ssrf`
2. Players attack the live infrastructure and submit the flag in the matching CTFd
3. Tear down when done: `cnimbus aws destroy --app-id ec2_ssrf`

Each challenge description in CTFd includes the corresponding `cnimbus` deploy
command, so the operator just needs to deploy the relevant labs before the event.
