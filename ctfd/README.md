# CTFd for Cumulonimbus

Spin up a self-hosted CTFd instance pre-loaded with all Cumulonimbus challenges.

## Quick Start

```bash
# 1. Start CTFd (from this directory)
docker compose up -d

# 2. Open http://localhost:8000 and complete the setup wizard
#    (create an admin account, set event name, etc.)

# 3. Generate an admin API token
#    Admin Panel > Settings > Access Tokens > Generate

# 4. Seed all challenges
python seed_challenges.py --url http://localhost:8000 --admin-token <your_token>
```

## Ports

| Service | Port |
|---------|------|
| CTFd UI | 8000 |
| MariaDB | internal only |
| Redis   | internal only |

## Teardown

```bash
docker compose down -v   # -v removes volumes (wipes scores and uploads)
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CTFD_SECRET_KEY` | `change-me-in-production` | Flask secret key — set this for any non-local deployment |

## Workflow with Cumulonimbus

1. Deploy a lab: `cnimbus azure create --app-id managed_identity_abuse`
2. Players attack the live infrastructure and capture the flag string
3. Players submit the flag in CTFd at `http://localhost:8000`
4. Tear down when done: `cnimbus azure destroy --app-id managed_identity_abuse`

Each challenge description in CTFd includes the corresponding `cnimbus` deploy command,
so the operator just needs to deploy the relevant labs before the event starts.
