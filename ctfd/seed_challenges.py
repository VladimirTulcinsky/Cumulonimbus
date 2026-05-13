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
        "name": "Lambda Environment Variable Secrets",
        "category": "AWS Serverless",
        "description": (
            "A developer stored a production API key directly in a Lambda function's "
            "environment variables. An 'auditor' IAM user has lambda:GetFunction, which "
            "returns the full function configuration including all environment variables "
            "in plaintext. Find the function and extract the secret.\n\n"
            "Deploy with: `cnimbus aws create --app-id lambda_env_secrets`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{L4mbd4_3nv_S3cr3ts_Pl41nt3xt}",
        "tags": ["AWS", "Lambda", "Credential Exposure", "Serverless", "Beginner"],
        "hints": [
            {"content": "Run aws lambda list-functions to find the target, then aws lambda get-function-configuration.", "cost": 0},
            {"content": "The response includes a .Environment.Variables field with all env vars in plaintext.", "cost": 25},
        ],
    },
    {
        "name": "Secrets Manager Over-Permissive Policy",
        "category": "AWS IAM",
        "description": (
            "A monitoring service account was granted secretsmanager:GetSecretValue with "
            "a wildcard resource path instead of a specific secret ARN. Combined with "
            "secretsmanager:ListSecrets, this allows enumerating and reading every secret "
            "under the /cumulonimbus/ prefix — including the flag.\n\n"
            "Deploy with: `cnimbus aws create --app-id secrets_manager_enum`"
        ),
        "value": 200,
        "type": "standard",
        "flag": "CUMULONIMBUS{S3cr3ts_M4n4g3r_0v3rp3rm1ss1v3}",
        "tags": ["AWS", "Secrets Manager", "IAM", "Misconfiguration"],
        "hints": [
            {"content": "Use aws secretsmanager list-secrets to enumerate all secrets your identity can see.", "cost": 0},
            {"content": "Call aws secretsmanager get-secret-value for each listed secret ARN.", "cost": 25},
        ],
    },
    {
        "name": "Terraform State File Exposure",
        "category": "Azure Storage",
        "description": (
            "An Azure Blob Storage container used as a Terraform backend was configured "
            "with container_access_type = 'blob' (public read). The state file contains "
            "multiple outputs marked sensitive=true — but Terraform's sensitive flag only "
            "suppresses CLI display; values are always stored in plaintext in .tfstate. "
            "Download the state file and extract the credentials.\n\n"
            "Deploy with: `cnimbus azure create --app-id terraform_state_exposure`"
        ),
        "value": 200,
        "type": "standard",
        "flag": "CUMULONIMBUS{TF_St4t3_S3ns1t1v3_1s_N0t_3ncrypt3d}",
        "tags": ["Azure", "Terraform", "Storage", "Credentials in State", "Intermediate"],
        "hints": [
            {"content": "The state blob URL is provided in the lab output. Download it with curl — no authentication required.", "cost": 0},
            {"content": "Parse the JSON and look inside .outputs. All values including sensitive=true ones are plaintext.", "cost": 25},
        ],
    },
    {
        "name": "EC2 User Data Secret Exposure",
        "category": "AWS Compute",
        "description": (
            "A developer hardcoded database credentials and an API secret in an EC2 "
            "instance's user data bootstrap script, intending to move them to SSM later. "
            "You have ec2:DescribeInstances and ec2:DescribeInstanceAttribute — enough "
            "to retrieve the full user data without SSH or console access.\n\n"
            "Deploy with: `cnimbus aws create --app-id ec2_userdata_secrets`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{3c2_Us3rD4t4_S3cr3ts_3xp0s3d}",
        "tags": ["AWS", "EC2", "User Data", "Credential Exposure", "Beginner"],
        "hints": [
            {"content": "Run aws ec2 describe-instances to get the instance ID.", "cost": 0},
            {"content": "aws ec2 describe-instance-attribute --attribute userData returns a base64 blob. Pipe it through 'base64 -d'.", "cost": 25},
        ],
    },
    {
        "name": "SSM Parameter Store Path Wildcard",
        "category": "AWS IAM",
        "description": (
            "A deployment agent IAM user was granted ssm:GetParametersByPath with a "
            "wildcard resource path covering the entire /cumulonimbus/ hierarchy instead "
            "of just the application config path it needs. Combined with kms:Decrypt, "
            "all SecureString parameters — including the flag — can be decrypted inline.\n\n"
            "Deploy with: `cnimbus aws create --app-id ssm_parameter_store`"
        ),
        "value": 200,
        "type": "standard",
        "flag": "CUMULONIMBUS{SSM_P4r4m3t3r_P4th_W1ldcard}",
        "tags": ["AWS", "SSM", "Parameter Store", "IAM", "Secrets Management"],
        "hints": [
            {"content": "Use aws ssm describe-parameters to enumerate all parameter names.", "cost": 0},
            {"content": "aws ssm get-parameters-by-path --path /cumulonimbus/ --recursive --with-decryption dumps all values including SecureString.", "cost": 25},
        ],
    },
    {
        "name": "ARM Deployment History Exposure",
        "category": "Azure ARM",
        "description": (
            "An ARM template was deployed with an admin API key passed as a plain 'string' "
            "parameter instead of 'secureString'. Azure retains full deployment history in "
            "the resource group. Any Reader can retrieve all parameter values from past "
            "deployments — including secrets that were never marked secure.\n\n"
            "Deploy with: `cnimbus azure create --app-id arm_deployment_history`"
        ),
        "value": 200,
        "type": "standard",
        "flag": "CUMULONIMBUS{4RM_D3pl0yment_H1st0ry_Pl41nt3xt}",
        "tags": ["Azure", "ARM", "Deployment History", "Credential Exposure"],
        "hints": [
            {"content": "Run az deployment group list --resource-group <rg> to see past deployments.", "cost": 0},
            {"content": "az deployment group show --name app-infra-v1 --query properties.parameters reveals all parameter values including plaintext string types.", "cost": 25},
        ],
    },
    {
        "name": "Exposed App Registration Client Secret",
        "category": "Azure Identity",
        "description": (
            "A developer stored an application config.json containing an Entra ID app "
            "registration's client_id and client_secret in a public Azure Blob Storage "
            "container. The service principal has Storage Blob Data Reader on a private "
            "storage account containing the flag. Find the config, extract the credentials, "
            "authenticate as the SP, and read the flag.\n\n"
            "Deploy with: `cnimbus azure create --app-id exposed_app_registration`"
        ),
        "value": 200,
        "type": "standard",
        "flag": "CUMULONIMBUS{3xp0s3d_4pp_R3g_Cl13nt_S3cr3t}",
        "tags": ["Azure", "App Registration", "Service Principal", "Credential Exposure"],
        "hints": [
            {"content": "Download the public config.json from the config blob URL — no auth required. The file contains Azure SP credentials.", "cost": 0},
            {"content": "az login --service-principal -u <client_id> -p <client_secret> --tenant <tenant_id>, then az storage blob download --auth-mode login", "cost": 25},
        ],
    },
    {
        "name": "S3 Public Access Misconfiguration",
        "category": "AWS Storage",
        "description": (
            "A developer disabled S3 Block Public Access on a data bucket and attached a "
            "bucket policy that grants s3:GetObject to the anonymous principal ('*'). "
            "You are given low-privilege IAM credentials that can only list buckets. "
            "Enumerate the bucket and read the flag without using your IAM identity.\n\n"
            "Deploy with: `cnimbus aws create --app-id s3_public_access`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{S3_Publ1c_Acc3ss_Bl0ck_D1sabl3d}",
        "tags": ["AWS", "S3", "Storage", "Misconfiguration", "Beginner"],
        "hints": [
            {"content": "Configure the attacker profile and run 'aws s3 ls' to discover the bucket.", "cost": 0},
            {"content": "Try 'aws s3 ls s3://<bucket> --no-sign-request' — the --no-sign-request flag sends the request anonymously.", "cost": 25},
        ],
    },
    {
        "name": "IAM Privilege Escalation via PassRole + Lambda",
        "category": "AWS IAM",
        "description": (
            "A developer IAM user has iam:PassRole scoped to a Lambda execution role with "
            "S3 read access on a private flag bucket, combined with lambda:CreateFunction "
            "and lambda:InvokeFunction. This is a well-known privilege escalation path: "
            "create a Lambda function that runs as the privileged role and reads the flag.\n\n"
            "Deploy with: `cnimbus aws create --app-id iam_privesc`"
        ),
        "value": 400,
        "type": "standard",
        "flag": "CUMULONIMBUS{1AM_Pass_R0l3_L4mbda_Pr1v3sc}",
        "tags": ["AWS", "IAM", "Lambda", "Privilege Escalation", "PassRole"],
        "hints": [
            {"content": "Check your permissions with aws iam get-user-policy. Notice iam:PassRole and lambda:CreateFunction together.", "cost": 25},
            {"content": "Create a Lambda with the privileged role ARN (--role flag). The handler just needs boto3 to read from S3.", "cost": 75},
        ],
    },
    {
        "name": "Automation Account Runbook Abuse",
        "category": "Azure Automation",
        "description": (
            "An Azure Automation Account has a system-assigned managed identity with "
            "Storage Blob Data Reader on a private flag storage account. "
            "You have been granted Automation Contributor — you can create and run runbooks. "
            "Runbooks execute as the Automation Account's managed identity. "
            "Write a PowerShell runbook that queries IMDS for a token and reads the flag.\n\n"
            "Deploy with: `cnimbus azure create --app-id automation_account`"
        ),
        "value": 250,
        "type": "standard",
        "flag": "CUMULONIMBUS{Aut0m4t10n_Runb00k_M1_Abus3}",
        "tags": ["Azure", "Automation", "Managed Identity", "IMDS", "Runbook"],
        "hints": [
            {"content": "Automation Contributor lets you create and publish runbooks that run as the Automation Account's managed identity.", "cost": 25},
            {"content": "In your runbook, call Invoke-RestMethod against http://169.254.169.254/metadata/identity/oauth2/token with resource=https://storage.azure.com/", "cost": 50},
        ],
    },
    {
        "name": "Azure Function App SSRF to IMDS",
        "category": "Azure Serverless",
        "description": (
            "An Azure Function App exposes a /api/fetch endpoint that proxies any ?url= "
            "the caller provides, without URL validation. The Function App has a "
            "system-assigned managed identity with Storage Blob Data Reader on a private "
            "blob container. Use SSRF to reach the Instance Metadata Service, obtain an "
            "OAuth token, and use it to read the flag from blob storage.\n\n"
            "Deploy with: `cnimbus azure create --app-id function_ssrf`"
        ),
        "value": 250,
        "type": "standard",
        "flag": "CUMULONIMBUS{Funct10n_SSRF_1MDS_T0k3n}",
        "tags": ["Azure", "Function App", "SSRF", "IMDS", "Managed Identity"],
        "hints": [
            {"content": "Probe the ?url= parameter with http://169.254.169.254/metadata/instance to confirm SSRF.", "cost": 0},
            {"content": "Fetch http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://storage.azure.com/ through the SSRF endpoint.", "cost": 25},
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
