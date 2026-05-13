# CTFd for Cumulonimbus

Spin up a self-hosted CTFd instance pre-loaded with all Cumulonimbus challenges.

## Quick Start

```bash
# 1. Start CTFd (from this directory)
docker compose up -d

# 2. Set up CTFd and seed all challenges automatically
python setup.py
```

That's it. `setup.py` waits for CTFd to become ready, completes the setup wizard,
generates an admin API token, and seeds all challenges in one step.

Open **http://localhost:8000** when it finishes. Default credentials: `admin` / `cumulonimbus`.

### Custom credentials / event name

```bash
python setup.py \
  --ctf-name   "My Cloud CTF" \
  --admin-name  admin \
  --admin-email admin@example.com \
  --admin-password supersecret
```

### Manual seeding (if CTFd is already configured)

```bash
# Generate a token via: Admin Panel > Settings > Access Tokens > Generate
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
