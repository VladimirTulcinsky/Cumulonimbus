#!/usr/bin/env python3
"""
Seed CTFd with Cumulonimbus challenges.

Usage:
    python seed_challenges.py --url http://localhost:8000 \
                               --admin-token <ctfd_admin_token>

The admin token is generated in CTFd under Admin Panel > Settings > Access Tokens.
Run this script after CTFd is up and you have completed the initial setup wizard.
"""

import argparse
import sys
import requests

CHALLENGES = [
    {
        "name": "EC2 SSRF",
        "category": "AWS",
        "description": (
            "A Node.js recipe application is running on an EC2 instance. "
            "The `/recipe?url=` endpoint fetches any URL the user provides. "
            "Abuse this to reach the EC2 Instance Metadata Service and exfiltrate "
            "credentials that allow you to read a private S3 object.\n\n"
            "Deploy with: `cnimbus aws create --app-id ec2_ssrf`"
        ),
        "value": 200,
        "type": "standard",
        "flag": "Cumulonimbus{Th4tW4sCh33sy}",
        "tags": ["SSRF", "AWS", "EC2", "IMDS", "S3"],
        "hints": [
            {"content": "The IMDS endpoint is at http://169.254.169.254/latest/meta-data/", "cost": 25},
            {"content": "Look for IAM credentials under /latest/meta-data/iam/security-credentials/", "cost": 50},
        ],
    },
    {
        "name": "Storage Account Public Access",
        "category": "Azure Storage",
        "description": (
            "A company left several Azure Storage containers misconfigured. "
            "One container uses 'container' access (full listing), leaking the location "
            "of a second container that uses 'blob' access only. "
            "Find and read the flag blob without any credentials.\n\n"
            "Deploy with: `cnimbus azure create --app-id sa_public_access`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{St0r4g3_Acc0unt_4cc355}",
        "tags": ["Azure", "Storage", "Misconfiguration", "Enumeration"],
        "hints": [
            {"content": "Use cloud-enum or az storage blob list to enumerate containers.", "cost": 25},
            {"content": "The config.cfg file in the 'website' container tells you where to look next.", "cost": 50},
        ],
    },
    {
        "name": "Cloud Shell Storage",
        "category": "Azure Storage",
        "description": (
            "Azure Cloud Shell persists its environment via a file share mounted to a storage account. "
            "A user's storage account has insufficient RBAC controls. "
            "Mount the Cloud Shell disk image and extract the flag from it.\n\n"
            "Deploy with: `cnimbus azure create --app-id cloudshell`"
        ),
        "value": 150,
        "type": "standard",
        "flag": "Cumulonimbus{CSStorageMustBeLockedDown}",
        "tags": ["Azure", "Cloud Shell", "Storage", "RBAC"],
        "hints": [
            {"content": "List file shares in the storage account. You're looking for a .img file.", "cost": 25},
            {"content": "Download the .img file and mount it: sudo mount -o loop acc_noher.img /mnt/cloudshell", "cost": 50},
        ],
    },
    {
        "name": "Add Service Principal Credentials",
        "category": "Azure Identity",
        "description": (
            "A user was removed as owner of an Azure AD application registration, "
            "but NOT from the underlying service principal. "
            "This oversight lets them add new credentials to the service principal "
            "and use it to join a privileged group.\n\n"
            "Deploy with: `cnimbus azure create --app-id add_sp_credentials`"
        ),
        "value": 300,
        "type": "standard",
        "flag": "CUMULONIMBUS{SP_Cr3d3nt14ls_4dd3d}",
        "tags": ["Azure", "Azure AD", "Service Principal", "Privilege Escalation"],
        "hints": [
            {"content": "Check if your user owns any service principals even after being removed from the app registration.", "cost": 25},
            {"content": "az ad sp credential reset lets you add a new secret to a service principal you own.", "cost": 50},
        ],
    },
    {
        "name": "Family Refresh Token (FOCI)",
        "category": "Azure Identity",
        "description": (
            "Microsoft's Family of Client IDs (FOCI) allows a refresh token obtained "
            "for one Microsoft application to be redeemed against a different client ID. "
            "Simulate device code phishing to get a token, then pivot to a privileged "
            "application scope and add yourself to an admin group.\n\n"
            "Deploy with: `cnimbus azure create --app-id foci`"
        ),
        "value": 300,
        "type": "standard",
        "flag": "CUMULONIMBUS{F4m1ly_R3fr3sh_T0k3n_4bus3d}",
        "tags": ["Azure", "OAuth", "FOCI", "Refresh Token", "Device Code Phishing"],
        "hints": [
            {"content": "Use TokenTactics or roadrecon to exchange the refresh token across client IDs.", "cost": 25},
            {"content": "Target the Teams or Azure PowerShell client ID to get elevated Graph scopes.", "cost": 50},
        ],
    },
    {
        "name": "Illicit Consent Grant",
        "category": "Azure Identity",
        "description": (
            "Craft an OAuth phishing URL that requests dangerous delegated permissions "
            "(mail.read, files.readWrite.all, AppRoleAssignment.ReadWrite.All). "
            "Trick the simulated admin into granting consent, then use your access token "
            "to read their mail and escalate privileges.\n\n"
            "Deploy with: `cnimbus azure create --app-id illicit_consent_grant`"
        ),
        "value": 250,
        "type": "standard",
        "flag": "CUMULONIMBUS{1ll1c1t_C0ns3nt_Gr4nt3d}",
        "tags": ["Azure", "OAuth", "Phishing", "Consent Grant", "Graph API"],
        "hints": [
            {"content": "Use the o365-attack-toolkit Docker image to build the phishing URL.", "cost": 25},
            {"content": "After consent is granted, your redirect URI receives an authorization code — exchange it for tokens.", "cost": 50},
        ],
    },
    {
        "name": "Shared Key Authentication",
        "category": "Azure Storage",
        "description": (
            "An Azure Function App uses Shared Key authentication to access a storage account. "
            "Source code stored in that storage account can be modified by anyone who "
            "discovers the account key. Tamper with the function code to make it leak "
            "a managed identity token, then use the token to read the flag from Key Vault.\n\n"
            "Deploy with: `cnimbus azure create --app-id shared_key_auth`"
        ),
        "value": 350,
        "type": "standard",
        "flag": "Cumulonimbus{SharedKeyAuthorizationShouldBeDisabled}",
        "tags": ["Azure", "Function App", "Storage", "Managed Identity", "Key Vault"],
        "hints": [
            {"content": "Enumerate storage accounts with the shared key. List the function app's code blob.", "cost": 25},
            {"content": "Replace the function code to call IMDS and return the token, then redeploy.", "cost": 75},
        ],
    },
    {
        "name": "Key Vault Misconfiguration",
        "category": "Azure Key Vault",
        "description": (
            "An Azure Key Vault was deployed in access policy mode with an overly permissive "
            "policy that accidentally grants an attacker user Get and List on secrets. "
            "The vault has public network access enabled. "
            "Log in as the attacker, discover the vault, and read the flag secret.\n\n"
            "Deploy with: `cnimbus azure create --app-id keyvault_misconfig`"
        ),
        "value": 200,
        "type": "standard",
        "flag": "CUMULONIMBUS{K3yV4ult_4cc3ss_P0l1cy_T00_Br04d}",
        "tags": ["Azure", "Key Vault", "Access Policy", "Misconfiguration"],
        "hints": [
            {"content": "Use `az keyvault list` to enumerate vaults in the resource group.", "cost": 25},
            {"content": "Run `az keyvault secret list` then `az keyvault secret show` to read the flag.", "cost": 50},
        ],
    },
    {
        "name": "Blob SAS Token Exposure",
        "category": "Azure Storage",
        "description": (
            "A developer hardcoded an Azure Blob Storage SAS token inside app.js, "
            "which is served publicly from a static website container. "
            "The token has read+list permissions on the entire storage account. "
            "Inspect the JavaScript source, extract the SAS token, "
            "and use it to access the private 'secrets' container.\n\n"
            "Deploy with: `cnimbus azure create --app-id blob_sas_abuse`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{SAS_T0k3n_N3v3r_1n_C0d3}",
        "tags": ["Azure", "Storage", "SAS Token", "Credential Exposure", "Beginner"],
        "hints": [
            {"content": "View the page source of the web app endpoint and look inside app.js for a SAS_TOKEN variable.", "cost": 0},
            {"content": "Use the SAS token to list the 'secrets' container: GET /secrets?restype=container&comp=list&<sas>", "cost": 25},
        ],
    },
    {
        "name": "Managed Identity Abuse",
        "category": "Azure Compute",
        "description": (
            "A VM is deployed with a system-assigned managed identity that has "
            "Storage Blob Data Reader on a private storage account containing the flag. "
            "You have been granted Virtual Machine Contributor on the VM — "
            "use `az vm run-command invoke` to query the Instance Metadata Service "
            "and obtain a storage-scoped OAuth token, then read the flag.\n\n"
            "Deploy with: `cnimbus azure create --app-id managed_identity_abuse`"
        ),
        "value": 250,
        "type": "standard",
        "flag": "CUMULONIMBUS{M4n4g3d_1d3nt1ty_4bus3}",
        "tags": ["Azure", "Managed Identity", "IMDS", "VM", "Storage"],
        "hints": [
            {"content": "Virtual Machine Contributor includes the RunCommand action — you can execute shell commands on the VM.", "cost": 25},
            {"content": "Query http://169.254.169.254/metadata/identity/oauth2/token?resource=https://storage.azure.com/ from inside the VM.", "cost": 50},
        ],
    },
]


def get_headers(token):
    return {"Authorization": f"Token {token}", "Content-Type": "application/json"}


def create_challenge(base_url, headers, challenge):
    payload = {
        "name": challenge["name"],
        "category": challenge["category"],
        "description": challenge["description"],
        "value": challenge["value"],
        "type": challenge["type"],
        "state": "visible",
    }
    resp = requests.post(f"{base_url}/api/v1/challenges", json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()["data"]["id"]


def create_flag(base_url, headers, challenge_id, flag_value):
    payload = {
        "challenge_id": challenge_id,
        "content": flag_value,
        "type": "static",
        "data": "",
    }
    resp = requests.post(f"{base_url}/api/v1/flags", json=payload, headers=headers)
    resp.raise_for_status()


def create_tags(base_url, headers, challenge_id, tags):
    for tag in tags:
        payload = {"challenge_id": challenge_id, "value": tag}
        resp = requests.post(f"{base_url}/api/v1/tags", json=payload, headers=headers)
        resp.raise_for_status()


def create_hints(base_url, headers, challenge_id, hints):
    for hint in hints:
        payload = {
            "challenge_id": challenge_id,
            "content": hint["content"],
            "cost": hint["cost"],
            "type": "standard",
        }
        resp = requests.post(f"{base_url}/api/v1/hints", json=payload, headers=headers)
        resp.raise_for_status()


def seed(base_url, token):
    headers = get_headers(token)

    # Verify connectivity
    resp = requests.get(f"{base_url}/api/v1/challenges", headers=headers)
    if resp.status_code == 403:
        print("ERROR: Invalid token or CTFd setup not yet complete.")
        sys.exit(1)
    resp.raise_for_status()

    existing = {c["name"] for c in resp.json().get("data", [])}

    for challenge in CHALLENGES:
        if challenge["name"] in existing:
            print(f"  [skip]    {challenge['name']} (already exists)")
            continue

        challenge_id = create_challenge(base_url, headers, challenge)
        create_flag(base_url, headers, challenge_id, challenge["flag"])
        create_tags(base_url, headers, challenge_id, challenge.get("tags", []))
        create_hints(base_url, headers, challenge_id, challenge.get("hints", []))
        print(f"  [created] {challenge['name']} (id={challenge_id})")

    print("\nSeeding complete.")


def main():
    parser = argparse.ArgumentParser(description="Seed CTFd with Cumulonimbus challenges")
    parser.add_argument("--url", default="http://localhost:8000",
                        help="Base URL of the CTFd instance (default: http://localhost:8000)")
    parser.add_argument("--admin-token", required=True, dest="token",
                        help="CTFd admin API token (Admin Panel > Settings > Access Tokens)")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    print(f"Seeding challenges into {base_url} ...\n")
    seed(base_url, args.token)


if __name__ == "__main__":
    main()
