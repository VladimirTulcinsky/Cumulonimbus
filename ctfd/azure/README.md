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

## Single instance only

This is a **singleton** — there can be only one. Resource names are fixed (the
resource group is always `cumulonimbus-ctfd`), so once it's deployed, any second
`terraform apply` from a different state fails with an "already exists" error
instead of standing up a duplicate scoreboard. To move/recreate it, the holder of
the current state must `terraform destroy` (or import the existing instance)
first.

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

The easiest way is from the **Cumulonimbus shell**: choose *Start the CTFd
scoreboard (Azure)*. It reuses your Azure login, prompts for the allowed CIDR and
an admin password, generates an SSH key, and runs the Terraform below for you.

To run it by hand instead:

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

> The VM clones the repo to get the `ctfd/` files, so `git_ref` must point at a
> ref that contains them. It currently defaults to the feature branch
> (`claude/enhance-cumulonimbus-lab-57qh7`); change it to `main` once this work is
> merged there. Override with `-var "git_ref=<ref>"` / `-var "repo_url=..."`.

## Useful variables

| Variable | Default | Notes |
|----------|---------|-------|
| `location` | `West Europe` | Azure region |
| `vm_size` | `Standard_B2s` | 2 vCPU / 4 GB — fine for CTFd + MariaDB + Redis |
| `player_allowed_cidr` | `0.0.0.0/0` | Who can reach the scoreboard (port 8001) |
| `ssh_allowed_cidr` | `0.0.0.0/0` | Restrict to your IP for SSH (port 22) |
| `ctfd_admin_password` | `cumulonimbus` | **Change this** |
| `repo_url` / `git_ref` | this repo / feature branch | Ref to clone; must contain `ctfd/` |

## Adjusting who can reach it

Set the initial allowed range at deploy time with `-var "player_allowed_cidr=..."`.
After it's up, you can also change it from the **Cumulonimbus shell**: choose
*Set CTFd scoreboard access (CIDR)* — it suggests your current public IP, and lets
you enter a custom CIDR or open it to the internet, then updates the running
instance's NSG rule. That's a live change via `az`; to make it permanent, set
`player_allowed_cidr` here and re-apply (otherwise the next `terraform apply`
resets it).

## SSH access

SSH requires the **private key** that matches the public key the VM was built
with — `ssh` without `-i` will fail with `Permission denied (publickey)`.

- **Deployed from the Cumulonimbus shell:** the key was generated at
  `app/cumulonimbus/.data/.ssh/ctfd_admin` (inside the container), and the deploy
  prints the exact command. Connect with:
  ```bash
  ssh -i /root/app/cumulonimbus/.data/.ssh/ctfd_admin ctfdadmin@<vm-ip>
  ```
- **Deployed by hand:** use the private key matching the `admin_ssh_public_key`
  you passed, e.g. `ssh -i ~/.ssh/id_rsa ctfdadmin@<vm-ip>`.

> The shell-generated key lives in the container's `.data`, which is ephemeral.
> If that container is gone, reset access with the public key you still have:
> `az vm user update -g cumulonimbus-ctfd -n ctfd-vm -u ctfdadmin --ssh-key-value "$(cat <pubkey>)"`.

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
