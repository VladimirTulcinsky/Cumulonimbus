# Persistent shared CTFd on Azure

Stands up **one shared CTFd scoreboard** on an Azure VM so it stays up
independently of anyone's laptop — players reach it at `http://<vm-ip>:8001` and
each gets their own CTFd account, score, and solve history on that single
instance.

This deploys ordinary (non-vulnerable) infrastructure — it's the scoreboard, not
a lab. It reuses the repo's `ctfd/docker-compose.yml` and `ctfd/setup.py`: the VM
installs Docker on first boot, clones the repo, and seeds the Azure challenges.
Data lives in Docker named volumes on the VM disk, and the containers run with
`restart: unless-stopped`, so the scoreboard and its data survive reboots.

## Prerequisites

- Terraform.
- A service principal (the same one you use for the labs works) with
  **Contributor or Owner on the subscription**. Export its credentials:
  ```bash
  export ARM_CLIENT_ID=<appId>
  export ARM_CLIENT_SECRET=<secret>
  export ARM_TENANT_ID=<tenant>
  export ARM_SUBSCRIPTION_ID=<subscription>
  ```
- An SSH public key (for admin access to the VM).

## Deploy

```bash
cd ctfd/azure
terraform init
terraform apply \
  -var "admin_ssh_public_key=$(cat ~/.ssh/id_rsa.pub)" \
  -var "ctfd_admin_password=<choose-a-strong-password>"
```

When it finishes, Terraform prints the scoreboard URL:

```
ctfd_url = "http://<public-ip>:8001"
```

First boot installs Docker, clones the repo, and seeds CTFd, so give it a few
minutes after `apply` before the URL responds. Log in as `admin` with the
password you set.

> By default the challenges/points come from the `main` branch. To seed from a
> different branch (e.g. while this work is on a feature branch), add
> `-var "git_ref=<branch>"`. Point at your own fork with `-var "repo_url=..."`.

## Useful variables

| Variable | Default | Notes |
|----------|---------|-------|
| `location` | `West Europe` | Azure region |
| `vm_size` | `Standard_B2s` | 2 vCPU / 4 GB — fine for CTFd + MariaDB + Redis |
| `player_allowed_cidr` | `0.0.0.0/0` | Who can reach the scoreboard (port 8001) |
| `ssh_allowed_cidr` | `0.0.0.0/0` | Restrict to your IP for SSH (port 22) |
| `ctfd_admin_password` | `cumulonimbus` | **Change this** |
| `repo_url` / `git_ref` | this repo / `main` | Source of the seeded challenges |

## Teardown

```bash
terraform destroy -var "admin_ssh_public_key=$(cat ~/.ssh/id_rsa.pub)"
```

## Notes & caveats

- **Cost:** a `Standard_B2s` VM, managed disk, and static public IP bill while
  running (roughly a few dollars a week). `terraform destroy` when the event is
  over; deallocating the VM stops compute charges but keeps the disk.
- **HTTP only:** the scoreboard is served over plain HTTP on port 8001. That's
  fine for a lab/classroom; put it behind a reverse proxy / TLS if you need it.
- **Exposure:** with the default `0.0.0.0/0`, the scoreboard (and SSH) are
  reachable from the internet. Restrict `player_allowed_cidr` / `ssh_allowed_cidr`
  if you can (e.g. your campus/VPN range). SSH is key-only (no password).
- **One instance, many users:** this is intentionally a single shared scoreboard.
  Each player just registers their own CTFd account on it.
