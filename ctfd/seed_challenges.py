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
        "category": "Compute",
        "description": (
            "A Node.js recipe application is running on an EC2 instance. "
            "The `/recipe?url=` endpoint fetches any URL the user provides. "
            "Abuse this to reach the EC2 Instance Metadata Service and exfiltrate "
            "credentials that allow you to read a private S3 object.\n\n"
            "Deploy with: `cnimbus aws create --app-id ec2_ssrf`"
        ),
        "value": 100,
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
        "category": "Storage",
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
        "category": "Storage",
        "description": (
            "Azure Cloud Shell persists its environment via a file share mounted to a storage account. "
            "A user's storage account has insufficient RBAC controls. "
            "Mount the Cloud Shell disk image and extract the flag from it.\n\n"
            "Deploy with: `cnimbus azure create --app-id cloudshell`"
        ),
        "value": 100,
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
        "category": "Identity",
        "description": (
            "A user was removed as owner of an Azure AD application registration, "
            "but NOT from the underlying service principal. "
            "This oversight lets them add new credentials to the service principal "
            "and use it to join a privileged group — whose membership grants Key "
            "Vault access where the flag is stored.\n\n"
            "Deploy with: `cnimbus azure create --app-id add_sp_credentials`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{SP_0wn3rsh1p_T0_K3yV4ult_Acc3ss}",
        "tags": ["Azure", "Azure AD", "Service Principal", "Privilege Escalation"],
        "hints": [
            {"content": "Check if your user owns any service principals even after being removed from the app registration.", "cost": 25},
            {"content": "az ad sp credential reset lets you add a new secret to a service principal you own.", "cost": 50},
        ],
    },
    {
        "name": "Family Refresh Token (FOCI)",
        "category": "Identity",
        "description": (
            "Microsoft's Family of Client IDs (FOCI) allows a refresh token obtained "
            "for one Microsoft application to be redeemed against a different client ID. "
            "Simulate device code phishing to get a token, then pivot to a privileged "
            "application scope and add yourself to an admin group.\n\n"
            "Deploy with: `cnimbus azure create --app-id foci`"
        ),
        "value": 100,
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
        "category": "Identity",
        "description": (
            "Craft an OAuth phishing URL that requests dangerous delegated permissions "
            "(mail.read, files.readWrite.all, AppRoleAssignment.ReadWrite.All). "
            "Trick the simulated admin into granting consent, then use your access token "
            "to read their mail and escalate privileges.\n\n"
            "Deploy with: `cnimbus azure create --app-id illicit_consent_grant`"
        ),
        "value": 100,
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
        "category": "Storage",
        "description": (
            "An Azure Function App uses Shared Key authentication to access a storage account. "
            "Source code stored in that storage account can be modified by anyone who "
            "discovers the account key. Tamper with the function code to make it leak "
            "a managed identity token, then use the token to read the flag from Key Vault.\n\n"
            "Deploy with: `cnimbus azure create --app-id shared_key_auth`"
        ),
        "value": 100,
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
        "category": "Serverless",
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
        "category": "Secrets",
        "description": (
            "A monitoring service account was granted secretsmanager:GetSecretValue with "
            "a wildcard resource path instead of a specific secret ARN. Combined with "
            "secretsmanager:ListSecrets, this allows enumerating and reading every secret "
            "under the /cumulonimbus/ prefix — including the flag.\n\n"
            "Deploy with: `cnimbus aws create --app-id secrets_manager_enum`"
        ),
        "value": 100,
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
        "category": "Infrastructure",
        "description": (
            "An Azure Blob Storage container used as a Terraform backend was configured "
            "with container_access_type = 'blob' (public read). The state file contains "
            "multiple outputs marked sensitive=true — but Terraform's sensitive flag only "
            "suppresses CLI display; values are always stored in plaintext in .tfstate. "
            "Download the state file and extract the credentials.\n\n"
            "Deploy with: `cnimbus azure create --app-id terraform_state_exposure`"
        ),
        "value": 100,
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
        "category": "Compute",
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
        "category": "Secrets",
        "description": (
            "A deployment agent IAM user was granted ssm:GetParametersByPath with a "
            "wildcard resource path covering the entire /cumulonimbus/ hierarchy instead "
            "of just the application config path it needs. Combined with kms:Decrypt, "
            "all SecureString parameters — including the flag — can be decrypted inline.\n\n"
            "Deploy with: `cnimbus aws create --app-id ssm_parameter_store`"
        ),
        "value": 100,
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
        "category": "Infrastructure",
        "description": (
            "An ARM template was deployed with an admin API key passed as a plain 'string' "
            "parameter instead of 'secureString'. Azure retains full deployment history in "
            "the resource group. Any Reader can retrieve all parameter values from past "
            "deployments — including secrets that were never marked secure.\n\n"
            "Deploy with: `cnimbus azure create --app-id arm_deployment_history`"
        ),
        "value": 100,
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
        "category": "Identity",
        "description": (
            "A developer stored an application config.json containing an Entra ID app "
            "registration's client_id and client_secret in a public Azure Blob Storage "
            "container. The service principal has Storage Blob Data Reader on a private "
            "storage account containing the flag. Find the config, extract the credentials, "
            "authenticate as the SP, and read the flag.\n\n"
            "Deploy with: `cnimbus azure create --app-id exposed_app_registration`"
        ),
        "value": 100,
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
        "category": "Storage",
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
        "category": "IAM",
        "description": (
            "A developer IAM user has iam:PassRole scoped to a Lambda execution role with "
            "S3 read access on a private flag bucket, combined with lambda:CreateFunction "
            "and lambda:InvokeFunction. This is a well-known privilege escalation path: "
            "create a Lambda function that runs as the privileged role and reads the flag.\n\n"
            "Deploy with: `cnimbus aws create --app-id iam_privesc`"
        ),
        "value": 100,
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
        "category": "Automation",
        "description": (
            "An Azure Automation Account has a system-assigned managed identity with "
            "Storage Blob Data Reader on a private flag storage account. "
            "You have been granted Automation Contributor — you can create and run runbooks. "
            "Runbooks execute as the Automation Account's managed identity. "
            "Write a PowerShell runbook that queries IMDS for a token and reads the flag.\n\n"
            "Deploy with: `cnimbus azure create --app-id automation_account`"
        ),
        "value": 100,
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
        "category": "Serverless",
        "description": (
            "An Azure Function App exposes a /api/fetch endpoint that proxies any ?url= "
            "the caller provides, without URL validation. The Function App has a "
            "system-assigned managed identity with Storage Blob Data Reader on a private "
            "blob container. Use SSRF to reach the Instance Metadata Service, obtain an "
            "OAuth token, and use it to read the flag from blob storage.\n\n"
            "Deploy with: `cnimbus azure create --app-id function_ssrf`"
        ),
        "value": 100,
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
        "category": "Key Vault",
        "description": (
            "An Azure Key Vault was deployed in access policy mode with an overly permissive "
            "policy that accidentally grants an attacker user Get and List on secrets. "
            "The vault has public network access enabled. "
            "Log in as the attacker, discover the vault, and read the flag secret.\n\n"
            "Deploy with: `cnimbus azure create --app-id keyvault_misconfig`"
        ),
        "value": 100,
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
        "category": "Storage",
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
        "category": "Identity",
        "description": (
            "A VM is deployed with a system-assigned managed identity that has "
            "Storage Blob Data Reader on a private storage account containing the flag. "
            "You have been granted Virtual Machine Contributor on the VM — "
            "use `az vm run-command invoke` to query the Instance Metadata Service "
            "and obtain a storage-scoped OAuth token, then read the flag.\n\n"
            "Deploy with: `cnimbus azure create --app-id managed_identity_abuse`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{M4n4g3d_1d3nt1ty_4bus3}",
        "tags": ["Azure", "Managed Identity", "IMDS", "VM", "Storage"],
        "hints": [
            {"content": "Virtual Machine Contributor includes the RunCommand action — you can execute shell commands on the VM.", "cost": 25},
            {"content": "Query http://169.254.169.254/metadata/identity/oauth2/token?resource=https://storage.azure.com/ from inside the VM.", "cost": 50},
        ],
    },
    {
        "name": "S3 Versioning — Deleted Object Recovery",
        "category": "Storage",
        "description": (
            "A developer accidentally committed production credentials to S3 inside "
            "`app/config.json`. They replaced the file and deleted it — thinking the "
            "history was gone. S3 versioning retains every version. Recover the original "
            "file and extract the flag.\n\n"
            "Deploy with: `cnimbus aws create --app-id s3_bucket_versioning`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{S3_V3rs10n1ng_D3l3t3d_0bj3cts}",
        "tags": ["AWS", "S3", "Versioning", "Enumeration"],
        "hints": [
            {"content": "Use `aws s3api list-object-versions` to see all versions including those before the delete marker.", "cost": 25},
            {"content": "Retrieve the earliest version with `aws s3api get-object --version-id <v1>`.", "cost": 50},
        ],
    },
    {
        "name": "CloudFormation Stack Output Exposure",
        "category": "Infrastructure",
        "description": (
            "An engineering team stored an API key directly in a CloudFormation stack "
            "Output. Any identity with `cloudformation:DescribeStacks` can read every "
            "output in plaintext. Find the stack and extract the flag.\n\n"
            "Deploy with: `cnimbus aws create --app-id cloudformation_stack`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{Cl0udF0rm4t10n_Outputs_Expos3_S3cr3ts}",
        "tags": ["AWS", "CloudFormation", "Secrets", "Enumeration"],
        "hints": [
            {"content": "Use `aws cloudformation list-stacks` to find the deployed stack.", "cost": 25},
            {"content": "Run `aws cloudformation describe-stacks --stack-name <name>` and inspect the Outputs section.", "cost": 50},
        ],
    },
    {
        "name": "STS AssumeRole — Wildcard Principal",
        "category": "IAM",
        "description": (
            "A role was created with `\"Principal\": {\"AWS\": \"*\"}` in the trust policy — "
            "meaning any AWS identity can assume it. The role has access to a secret SSM "
            "parameter. Enumerate the roles, assume the misconfigured one, and read the flag.\n\n"
            "Deploy with: `cnimbus aws create --app-id sts_assume_role_any`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{STS_Assum3_R0l3_W1ldcard_Pr1ncipal}",
        "tags": ["AWS", "IAM", "STS", "Privilege Escalation"],
        "hints": [
            {"content": "Use `aws iam list-roles` to find a cumulonimbus role with an overly permissive trust policy.", "cost": 25},
            {"content": "After assuming the role, read the flag from SSM: `aws ssm get-parameter --name /cumulonimbus/sts_assume_role_any/flag --with-decryption`.", "cost": 50},
        ],
    },
    {
        "name": "App Service Environment Variables",
        "category": "Web",
        "description": (
            "A team deployed an Azure App Service and stored credentials in Application "
            "Settings. Website Contributor includes `Microsoft.Web/sites/config/list` which "
            "returns all app settings in plaintext. List the settings and find the flag.\n\n"
            "Deploy with: `cnimbus azure create --app-id app_service_env_vars`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{App_S3rv1c3_Env_V4rs_3xp0s3d}",
        "tags": ["Azure", "App Service", "Secrets", "Configuration"],
        "hints": [
            {"content": "Use `az webapp config appsettings list --name <app> --resource-group <rg>` with your attacker credentials.", "cost": 25},
            {"content": "Look for the SECRET_FLAG key in the app settings output.", "cost": 50},
        ],
    },
    {
        "name": "Lambda Function URL — No Auth",
        "category": "Serverless",
        "description": (
            "A developer exposed an internal diagnostics Lambda function via a Function URL "
            "configured with `AuthType: NONE`. The function is publicly accessible without "
            "any AWS credentials. Call the URL and retrieve the flag from the JSON response.\n\n"
            "Deploy with: `cnimbus aws create --app-id lambda_function_url`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{L4mbd4_Funct10n_URL_N0_Auth}",
        "tags": ["AWS", "Lambda", "Serverless", "Exposure"],
        "hints": [
            {"content": "Lambda Function URLs with AuthType NONE are publicly accessible — no credentials needed.", "cost": 25},
            {"content": "Use `curl <function_url>` and look at the `flag` key in the JSON response body.", "cost": 50},
        ],
    },
    {
        "name": "Cognito Identity Pool — Unauthenticated Access",
        "category": "Identity",
        "description": (
            "A mobile app's Cognito Identity Pool allows unauthenticated (guest) identities "
            "with an overly permissive IAM role attached. Exchange the pool ID for temporary "
            "AWS credentials without any login, then use them to read the private S3 flag.\n\n"
            "Deploy with: `cnimbus aws create --app-id cognito_identity_pool`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{C0gn1t0_Un4uth_1d3nt1ty_AWS_Cr3ds}",
        "tags": ["AWS", "Cognito", "Identity", "S3", "Credential Abuse"],
        "hints": [
            {"content": "Use `aws cognito-identity get-id` with the identity pool ID to get an IdentityId without logging in.", "cost": 25},
            {"content": "Exchange the IdentityId for temporary STS credentials via `get-credentials-for-identity`, then use them to read the S3 flag object.", "cost": 50},
        ],
    },
    {
        "name": "Logic App — Hardcoded Credentials",
        "category": "Integration",
        "description": (
            "An Azure Logic App sends hourly notifications with a bearer token hardcoded in "
            "the HTTP action headers. Any identity with Reader on the resource group can "
            "retrieve the full workflow definition — including the Authorization header.\n\n"
            "Deploy with: `cnimbus azure create --app-id logic_app_credentials`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{L0g1c_App_H4rdcod3d_Cr3d3nt14ls}",
        "tags": ["Azure", "Logic App", "Secrets", "Integration"],
        "hints": [
            {"content": "Use `az logic workflow show` to retrieve the workflow JSON definition.", "cost": 25},
            {"content": "Inspect the `actions` section for the HTTP action headers — the Authorization value contains the flag.", "cost": 50},
        ],
    },
    {
        "name": "Storage Account Keys — Control Plane Bypass",
        "category": "Storage",
        "description": (
            "An attacker account has Storage Account Contributor — a control-plane role that "
            "also includes `listKeys`. Use the master key to bypass Azure RBAC entirely and "
            "read a private blob containing the flag.\n\n"
            "Deploy with: `cnimbus azure create --app-id storage_account_keys`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{St0r4g3_Acc0unt_K3ys_Byp4ss_RBAC}",
        "tags": ["Azure", "Storage", "RBAC", "Privilege Escalation"],
        "hints": [
            {"content": "Storage Account Contributor includes `listKeys` — use `az storage account keys list` to retrieve the account master key.", "cost": 25},
            {"content": "Use the account key with `az storage blob download --account-key <key>` to access the private container.", "cost": 50},
        ],
    },
    {
        "name": "S3 Object ACL — Public Read",
        "category": "Storage",
        "description": (
            "A developer set a `public-read` ACL on an individual S3 object. The bucket "
            "blocks public policies, but object-level ACLs bypass this — making the file "
            "directly accessible over HTTPS without any credentials.\n\n"
            "Deploy with: `cnimbus aws create --app-id s3_object_public_acl`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{S3_0bj3ct_ACL_Publ1c_R3ad}",
        "tags": ["AWS", "S3", "ACL", "Misconfiguration"],
        "hints": [
            {"content": "Object-level ACLs can make individual objects public even when the bucket blocks public bucket policies.", "cost": 25},
            {"content": "Fetch `public/release-notes.txt` directly: `curl https://<bucket>.s3.eu-west-1.amazonaws.com/public/release-notes.txt`", "cost": 50},
        ],
    },
    {
        "name": "Glue Job — Secrets in Arguments",
        "category": "Data",
        "description": (
            "An ETL team stored database credentials directly in a Glue job's "
            "`DefaultArguments`. These are returned in plaintext by `glue:GetJob`. "
            "Enumerate the job and extract the flag from the job arguments.\n\n"
            "Deploy with: `cnimbus aws create --app-id glue_job_secrets`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{Glu3_J0b_S3cr3ts_1n_4rgum3nts}",
        "tags": ["AWS", "Glue", "ETL", "Secrets"],
        "hints": [
            {"content": "Use `aws glue list-jobs` to find the job, then `aws glue get-job --job-name <name>`.", "cost": 25},
            {"content": "The flag is in the `--api-key` key inside `Job.DefaultArguments`.", "cost": 50},
        ],
    },
    {
        "name": "VM RunCommand — Arbitrary Execution",
        "category": "Compute",
        "description": (
            "An attacker account has Virtual Machine Contributor on a resource group. "
            "This role includes `runCommand/action`, allowing arbitrary shell execution "
            "on the VM as root — no SSH access needed. Read `/root/flag.txt` via RunCommand.\n\n"
            "Deploy with: `cnimbus azure create --app-id vm_run_command`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{VM_RunC0mm4nd_Arb1tr4ry_Exec}",
        "tags": ["Azure", "VM", "RunCommand", "Privilege Escalation"],
        "hints": [
            {"content": "Virtual Machine Contributor includes `Microsoft.Compute/virtualMachines/runCommand/action`.", "cost": 25},
            {"content": "Use `az vm run-command invoke --command-id RunShellScript --scripts 'cat /root/flag.txt'` to read the flag.", "cost": 50},
        ],
    },
    {
        "name": "Container Instance — Plaintext Env Vars",
        "category": "Containers",
        "description": (
            "An ACI container group stores a sensitive API key as a plain (non-secure) "
            "environment variable. Any Reader can retrieve the full container definition "
            "via ARM, including all non-secure environment variables.\n\n"
            "Deploy with: `cnimbus azure create --app-id container_instance_env`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{C0nt41n3r_1nst4nc3_Pl41nt3xt_Env}",
        "tags": ["Azure", "ACI", "Containers", "Secrets"],
        "hints": [
            {"content": "Use `az container show --name <name> --resource-group <rg>` to retrieve the container group definition.", "cost": 25},
            {"content": "Look for `SECRET_FLAG` in the `environmentVariables` array — non-secure env vars are returned in plaintext by the ARM API.", "cost": 50},
        ],
    },
    {
        "name": "Secrets Chain — Plaintext Credentials End to End",
        "category": "Credential Exposure",
        "description": (
            "A sequential lab that strings the 'plaintext credentials in a resource' "
            "scenarios into one attack path. Start as an anonymous visitor to a portal "
            "website whose app.js leaks a SAS token, then follow each leaked secret to "
            "the next resource: SAS → service principal → App Configuration → Data "
            "Factory storage key → Container Instance → Key Vault. The flag is the Key "
            "Vault secret at the end of the chain.\n\n"
            "Deploy with: `cnimbus azure create --app-id secrets_chain`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{Pl41nt3xt_Cr3d_Ch41n_2_K3yV4ult}",
        "tags": ["Azure", "Credential Exposure", "Chained", "SAS", "Key Vault"],
        "hints": [
            {"content": "Step 1 needs no credentials: read the portal website's app.js — it hardcodes a SAS token. Use it to list the account's containers and read the private 'onboarding' blob (service principal creds).", "cost": 25},
            {"content": "After `az login --service-principal`, follow the trail: resource-group tag → App Configuration (`az appconfig kv list`) → Data Factory linked-service connection string (storage key) → private 'runtime' blob → Container Instance env vars → `az keyvault secret show`.", "cost": 50},
        ],
    },
    {
        "name": "ACR Image Secrets — Leaked Admin Creds",
        "category": "Containers",
        "description": (
            "A private Azure Container Registry has its admin account enabled, and the "
            "credentials were left in a storage account's resource tags — readable by any "
            "Reader on the resource group. Use them to pull the application image, then "
            "recover the secret baked into it. The obvious config file in the running "
            "container is a decoy; the real flag was written into an image layer and only "
            "'deleted' in a later step, so it still ships inside the image.\n\n"
            "Deploy with: `cnimbus azure create --app-id acr_image_secrets`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{4CR_Adm1n_Cr3ds_2_D3l3t3d_L4y3r_S3cr3t}",
        "tags": ["Azure", "ACR", "Containers", "Secrets", "Images"],
        "hints": [
            {"content": "You only have Reader, so `az acr credential show` is denied — but the admin user/password were left in a storage account's tags. Check `az resource show ... --query tags`.", "cost": 25},
            {"content": "After `docker login` + `docker pull`, the runtime config (/app/config/app.config) is a rotated decoy. Recover the real DEPLOY_TOKEN from the deleted layer with `docker history --no-trunc` or `docker save` + grep.", "cost": 50},
        ],
    },
    {
        "name": "SQS Queue — Public Resource Policy",
        "category": "Messaging",
        "description": (
            "An SQS queue has a resource policy granting `sqs:ReceiveMessage` to "
            "`\"Principal\": \"*\"` — any caller. Messages containing sensitive data are "
            "visible to anyone with the queue URL. No AWS credentials required.\n\n"
            "Deploy with: `cnimbus aws create --app-id sqs_public_receive`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{SQS_Publ1c_R3s0urc3_P0l1cy_R3c31v3}",
        "tags": ["AWS", "SQS", "Messaging", "Misconfiguration"],
        "hints": [
            {"content": "The queue policy allows any principal to receive messages — no credentials needed, just the queue URL.", "cost": 25},
            {"content": "Run `aws sqs receive-message --queue-url <url> --region eu-west-1` — the flag is in the message body.", "cost": 50},
        ],
    },
    {
        "name": "SSM Session Manager — Shell Without SSH",
        "category": "Compute",
        "description": (
            "An EC2 instance has the SSM Agent running and an IAM user has "
            "`ssm:StartSession`. This allows opening an interactive root shell on "
            "the instance with no SSH key, no open ports, and no bastion host. "
            "Read `/root/flag.txt`.\n\n"
            "Deploy with: `cnimbus aws create --app-id ssm_session_manager`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{SSM_S3ss10n_M4n4g3r_Sh3ll_4cc3ss}",
        "tags": ["AWS", "SSM", "EC2", "Lateral Movement"],
        "hints": [
            {"content": "Use `aws ec2 describe-instances` to find the target instance ID, then `aws ssm start-session --target <id>`.", "cost": 25},
            {"content": "Once connected, run `sudo cat /root/flag.txt` to read the flag.", "cost": 50},
        ],
    },
    {
        "name": "Resource Group Tags — Credentials in Metadata",
        "category": "Governance",
        "description": (
            "A platform team stored a service principal secret as an Azure resource group "
            "tag. Tags are visible to any Reader on the resource. Enumerate the "
            "subscription's resource groups and find the flag in the tags.\n\n"
            "Deploy with: `cnimbus azure create --app-id resource_group_tags`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{S3cr3t_1n_R3s0urc3_Gr0up_T4gs}",
        "tags": ["Azure", "Tags", "Identity", "Secrets"],
        "hints": [
            {"content": "Use `az group list` to find the cumulonimbus resource group, then `az group show --name <rg> --query tags`.", "cost": 25},
            {"content": "The `service-principal-secret` tag contains the flag.", "cost": 50},
        ],
    },
    {
        "name": "Event Grid — Webhook Token Exposure",
        "category": "Integration",
        "description": (
            "An Event Grid subscription uses a secret token embedded in the webhook URL "
            "as a query parameter. The full URL is returned by the ARM API to any Reader. "
            "Find the subscription and extract the token from the webhook URL.\n\n"
            "Deploy with: `cnimbus azure create --app-id eventgrid_webhook_token`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{3v3ntGr1d_W3bh00k_T0k3n_3xp0s3d}",
        "tags": ["Azure", "Event Grid", "Webhook", "Secrets"],
        "hints": [
            {"content": "Use `az eventgrid event-subscription list --source-resource-id <topic-id>` to find subscriptions.", "cost": 25},
            {"content": "Run `az eventgrid event-subscription show --query \"destination.endpointUrl\"` — the `token` query parameter contains the flag.", "cost": 50},
        ],
    },
    {
        "name": "CodeBuild — Plaintext Environment Variables",
        "category": "CI-CD",
        "description": (
            "A CodeBuild project stores an API key as a PLAINTEXT environment variable. "
            "Unlike PARAMETER_STORE or SECRETS_MANAGER types, plaintext values are "
            "returned unmasked by `codebuild:BatchGetProjects`. Enumerate the project "
            "and extract the flag.\n\n"
            "Deploy with: `cnimbus aws create --app-id codebuild_env_vars`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{C0d3Bu1ld_Pl41nt3xt_Env_V4rs}",
        "tags": ["AWS", "CodeBuild", "CI/CD", "Secrets"],
        "hints": [
            {"content": "Use `aws codebuild list-projects` then `aws codebuild batch-get-projects --names <name>`.", "cost": 25},
            {"content": "The flag is in the `DEPLOY_API_KEY` entry of `projects[0].environment.environmentVariables`.", "cost": 50},
        ],
    },
    {
        "name": "Step Functions — Execution History Exposure",
        "category": "Serverless",
        "description": (
            "A Step Functions workflow passes sensitive payment data and an API key as "
            "execution input. The full input is retained in execution history for 90 days "
            "and is readable by anyone with `states:GetExecutionHistory`. Find the past "
            "execution and extract the flag.\n\n"
            "Deploy with: `cnimbus aws create --app-id stepfunctions_execution_history`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{St3pFunct10ns_3x3cut10n_H1st0ry_L34k}",
        "tags": ["AWS", "Step Functions", "Serverless", "Data Exposure"],
        "hints": [
            {"content": "Use `aws stepfunctions list-state-machines` to find the ARN, then `aws stepfunctions list-executions` to list past runs.", "cost": 25},
            {"content": "Run `aws stepfunctions get-execution-history --execution-arn <arn>` and look at the `ExecutionStarted` event's input — the `internalApiKey` field contains the flag.", "cost": 50},
        ],
    },
    {
        "name": "App Configuration — Data Reader Enumeration",
        "category": "Configuration",
        "description": (
            "An Azure App Configuration store contains database credentials and an API key "
            "alongside normal config. The attacker has App Configuration Data Reader and can "
            "list all key-values in plaintext. Find the `secrets/api-key` entry.\n\n"
            "Deploy with: `cnimbus azure create --app-id app_configuration_secrets`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{App_C0nf1g_D4t4_R34d3r_Enum}",
        "tags": ["Azure", "App Configuration", "Secrets", "Enumeration"],
        "hints": [
            {"content": "Use `az appconfig kv list --name <store> --auth-mode login` to list all key-values.", "cost": 25},
            {"content": "The flag is the value of the `secrets/api-key` key.", "cost": 50},
        ],
    },
    {
        "name": "VM Extension — Plaintext Settings",
        "category": "Compute",
        "description": (
            "A Custom Script Extension on a VM embeds a command in its `settings` block "
            "(not `protectedSettings`). The `settings` block is stored unencrypted in ARM "
            "and returned by any Reader. Inspect the extension to find the flag in "
            "`commandToExecute`.\n\n"
            "Deploy with: `cnimbus azure create --app-id vm_extension_settings`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{VM_3xt3ns10n_S3tt1ngs_Pl41nt3xt}",
        "tags": ["Azure", "VM Extension", "Custom Script", "Secrets"],
        "hints": [
            {"content": "Use `az vm extension list --vm-name <vm> --resource-group <rg>` to find the CustomScript extension.", "cost": 25},
            {"content": "Run `az vm extension show --name configure-app --query settings` — `commandToExecute` contains the flag.", "cost": 50},
        ],
    },
    {
        "name": "Route53 Records",
        "category": "Networking",
        "description": (
            "A developer stored a sensitive value inside a Route53 DNS TXT record. "
            "You have IAM credentials with Route53 read access. "
            "Enumerate the hosted zone records to find the flag.\n\n"
            "Deploy with: `cnimbus aws create --app-id route53_records`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{R0ut353_TXT_R3c0rd_S3cr3ts}",
        "tags": ["AWS", "Route53", "DNS", "Enumeration"],
        "hints": [
            {"content": "Use `aws route53 list-hosted-zones` to find the hosted zone ID.", "cost": 25},
            {"content": "Run `aws route53 list-resource-record-sets --hosted-zone-id <zone-id>` and look for a TXT record containing the flag.", "cost": 50},
        ],
    },
    {
        "name": "ECS Exec",
        "category": "Containers",
        "description": (
            "A Fargate service has `enable_execute_command` enabled. "
            "The attacker IAM user has `ecs:ExecuteCommand` and the SSM Messages permissions. "
            "Use ECS Exec to open a shell inside the running container and read the flag from `/flag.txt`.\n\n"
            "Deploy with: `cnimbus aws create --app-id ecs_exec`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{ECS_3x3c_C0nt41n3r_Sh3ll}",
        "tags": ["AWS", "ECS", "Fargate", "Container", "ECS Exec"],
        "hints": [
            {"content": "Use `aws ecs list-clusters` then `aws ecs list-tasks --cluster <name>` to find the running task.", "cost": 25},
            {"content": "Run `aws ecs execute-command --cluster <name> --task <id> --container app --interactive --command 'cat /flag.txt'`.", "cost": 50},
        ],
    },
    {
        "name": "APIM Named Value",
        "category": "API Management",
        "description": (
            "An Azure API Management instance has a Named Value stored in plaintext "
            "(secret = false). The attacker has Reader on the resource group. "
            "Read the Named Value to retrieve the flag.\n\n"
            "Deploy with: `cnimbus azure create --app-id apim_named_value`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{AP1M_N4m3d_V4lu3_Pl41nt3xt}",
        "tags": ["Azure", "API Management", "Named Value", "Secrets"],
        "hints": [
            {"content": "Use `az apim nv list --service-name <apim> --resource-group <rg>` to list Named Values.", "cost": 25},
            {"content": "Run `az apim nv show --service-name <apim> --resource-group <rg> --named-value-id flag-key --query value -o tsv`.", "cost": 50},
        ],
    },
    {
        "name": "Container App Env Vars",
        "category": "Containers",
        "description": (
            "A developer stored a secret flag directly in an Azure Container App's environment variables. "
            "The attacker has Reader on the resource group. "
            "Inspect the Container App definition to find the flag.\n\n"
            "Deploy with: `cnimbus azure create --app-id container_app_env_vars`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{C0nt41n3r_App_Env_V4rs_3xp0s3d}",
        "tags": ["Azure", "Container Apps", "Environment Variables", "Secrets"],
        "hints": [
            {"content": "Use `az containerapp list --resource-group <rg>` to find the Container App name.", "cost": 25},
            {"content": "Run `az containerapp show --name <name> --resource-group <rg> --query 'properties.template.containers[0].env'`.", "cost": 50},
        ],
    },
    {
        "name": "DynamoDB Scan",
        "category": "Database",
        "description": (
            "A developer stored a sensitive API key directly as a DynamoDB table item. "
            "The attacker IAM user has DynamoDB read access. "
            "Scan the table to find the flag.\n\n"
            "Deploy with: `cnimbus aws create --app-id dynamodb_scan`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{Dyn4m0DB_Sc4n_D4t4_3xp0sur3}",
        "tags": ["AWS", "DynamoDB", "Database", "Data Exposure"],
        "hints": [
            {"content": "Use `aws dynamodb list-tables` to find the target table.", "cost": 25},
            {"content": "Run `aws dynamodb scan --table-name <table-name>` and look at the `value` field of each item.", "cost": 50},
        ],
    },
    {
        "name": "Kinesis Shard Reader",
        "category": "Streaming",
        "description": (
            "A developer accidentally published a sensitive record to a Kinesis Data Stream. "
            "The attacker has Kinesis read permissions. "
            "Read the shard from the beginning, decode the base64 record data, and retrieve the flag.\n\n"
            "Deploy with: `cnimbus aws create --app-id kinesis_shard_reader`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{K1n3s1s_Sh4rd_R3c0rd_L34k}",
        "tags": ["AWS", "Kinesis", "Streaming", "Data Exposure"],
        "hints": [
            {"content": "Use `aws kinesis list-streams` then `aws kinesis get-shard-iterator --shard-iterator-type TRIM_HORIZON` to get a starting iterator.", "cost": 25},
            {"content": "Run `aws kinesis get-records --shard-iterator <iterator>` and base64-decode the `Data` field: `echo '<data>' | base64 -d`.", "cost": 50},
        ],
    },
    {
        "name": "Deployment Script",
        "category": "Infrastructure",
        "description": (
            "An Azure Deployment Script ran during infrastructure provisioning and wrote sensitive data to its outputs. "
            "The outputs are persisted in the ARM resource definition. "
            "The attacker has Reader on the resource group. Read the script outputs to retrieve the flag.\n\n"
            "Deploy with: `cnimbus azure create --app-id deployment_script`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{D3pl0ym3nt_Scr1pt_0utput_3xp0s3d}",
        "tags": ["Azure", "Deployment Script", "IaC", "Data Exposure"],
        "hints": [
            {"content": "Use `az deployment-scripts list --resource-group <rg>` to find the deployment script.", "cost": 25},
            {"content": "Run `az deployment-scripts show --name <name> --resource-group <rg> --query outputs`.", "cost": 50},
        ],
    },
    {
        "name": "Policy Assignment Metadata",
        "category": "Governance",
        "description": (
            "The platform team stored an internal reference token in an Azure Policy assignment's metadata field. "
            "Policy assignment metadata is plaintext and readable by any Reader. "
            "List policy assignments in the resource group and inspect the metadata to find the flag.\n\n"
            "Deploy with: `cnimbus azure create --app-id policy_assignment_metadata`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{P0l1cy_M3t4d4t4_S3cr3t_3xp0s3d}",
        "tags": ["Azure", "Policy", "Governance", "Secrets"],
        "hints": [
            {"content": "Use `az policy assignment list --resource-group <rg>` to list assignments scoped to the resource group.", "cost": 25},
            {"content": "Inspect the metadata field: `az policy assignment show --name <name> --resource-group <rg> --query metadata`.", "cost": 50},
        ],
    },
    {
        "name": "Amplify Env Vars",
        "category": "Frontend",
        "description": (
            "A developer stored a secret directly in an AWS Amplify app's environment variables. "
            "The attacker has Amplify read access. "
            "Retrieve the app definition to find the flag in the environment variables.\n\n"
            "Deploy with: `cnimbus aws create --app-id amplify_env_vars`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{4mpl1fy_App_3nv_V4rs_3xp0s3d}",
        "tags": ["AWS", "Amplify", "Environment Variables", "Secrets"],
        "hints": [
            {"content": "Use `aws amplify list-apps` to find the target Amplify application.", "cost": 25},
            {"content": "Run `aws amplify get-app --app-id <id> --query 'app.environmentVariables'` to read all environment variables.", "cost": 50},
        ],
    },
    {
        "name": "AppConfig Deployment",
        "category": "Configuration",
        "description": (
            "A developer stored database credentials inside an AWS AppConfig hosted configuration version. "
            "The attacker has AppConfig read access. "
            "Download the configuration content and find the flag embedded in the JSON.\n\n"
            "Deploy with: `cnimbus aws create --app-id appconfig_deployment`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{AppC0nf1g_H0st3d_C0nf1g_3xp0s3d}",
        "tags": ["AWS", "AppConfig", "Configuration", "Secrets"],
        "hints": [
            {"content": "Use `aws appconfig list-applications` then `aws appconfig list-configuration-profiles --application-id <id>`.", "cost": 25},
            {"content": "Run `aws appconfig get-hosted-configuration-version --application-id <id> --configuration-profile-id <id> --version-number 1 /tmp/config.json && cat /tmp/config.json`.", "cost": 50},
        ],
    },
    {
        "name": "Monitor Action Group",
        "category": "Monitoring",
        "description": (
            "An Azure Monitor Action Group has a webhook receiver whose URL contains an embedded authentication token. "
            "The attacker has Reader on the resource group. "
            "Read the Action Group definition to find the token in the webhook URL.\n\n"
            "Deploy with: `cnimbus azure create --app-id monitor_action_group`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{Monit0r_W3bh00k_T0k3n_3xp0s3d}",
        "tags": ["Azure", "Monitor", "Action Group", "Webhook", "Secrets"],
        "hints": [
            {"content": "Use `az monitor action-group list --resource-group <rg>` to find the action group.", "cost": 25},
            {"content": "Run `az monitor action-group show --name <name> --resource-group <rg> --query webhookReceivers` and look at the `serviceUri`.", "cost": 50},
        ],
    },
    {
        "name": "Data Factory Linked Service",
        "category": "Integration",
        "description": (
            "An Azure Data Factory linked service stores a storage account connection string in cleartext — "
            "without Key Vault integration. The attacker has Reader on the resource group. "
            "Read the linked service definition to extract the embedded account key.\n\n"
            "Deploy with: `cnimbus azure create --app-id data_factory_linked_service`"
        ),
        "value": 100,
        "type": "standard",
        "flag": "CUMULONIMBUS{ADF_L1nk3d_S3rv1c3_Cl34rt3xt_K3y}",
        "tags": ["Azure", "Data Factory", "Linked Service", "Connection String", "Secrets"],
        "hints": [
            {"content": "Use `az datafactory linked-service list --factory-name <name> --resource-group <rg>` to list linked services.", "cost": 25},
            {"content": "Run `az datafactory linked-service show --factory-name <name> --linked-service-name DataLakeConnection --resource-group <rg> --query 'properties.typeProperties.connectionString'`.", "cost": 50},
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


AWS_TAGS   = {"AWS"}
AZURE_TAGS = {"Azure"}

PROVIDER_DEFAULTS = {
    "aws":   "http://localhost:8000",
    "azure": "http://localhost:8001",
}


def filter_challenges(provider: str) -> list:
    """Return challenges whose tags include the given provider (case-insensitive)."""
    key = provider.lower()
    if key == "aws":
        return [c for c in CHALLENGES if AWS_TAGS & set(c.get("tags", []))]
    if key == "azure":
        return [c for c in CHALLENGES if AZURE_TAGS & set(c.get("tags", []))]
    return CHALLENGES


def seed(base_url, token, provider=None):
    headers = get_headers(token)

    # Verify connectivity
    resp = requests.get(f"{base_url}/api/v1/challenges", headers=headers)
    if resp.status_code == 403:
        print("ERROR: Invalid token or CTFd setup not yet complete.")
        sys.exit(1)
    resp.raise_for_status()

    existing = {c["name"] for c in resp.json().get("data", [])}
    challenges = filter_challenges(provider) if provider else CHALLENGES

    for challenge in challenges:
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
    parser.add_argument("--provider", choices=["aws", "azure"],
                        help="Seed only AWS or only Azure challenges (omit for all)")
    parser.add_argument("--url", default=None,
                        help="CTFd base URL (default: 8000 for AWS, 8001 for Azure)")
    parser.add_argument("--admin-token", required=True, dest="token",
                        help="CTFd admin API token (Admin Panel > Settings > Access Tokens)")
    args = parser.parse_args()

    default_url = PROVIDER_DEFAULTS.get(args.provider, "http://localhost:8000")
    base_url = (args.url or default_url).rstrip("/")
    label = args.provider.upper() if args.provider else "all"
    print(f"Seeding {label} challenges into {base_url} ...\n")
    seed(base_url, args.token, provider=args.provider)


if __name__ == "__main__":
    main()
