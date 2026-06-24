"""Spoiler-free descriptions for the Azure labs.

Shown in the interactive shell when a user asks for more information about a
lab, so they can decide what to play without being handed the solution. The
summaries intentionally describe the scenario and the class of weakness only —
they do not contain commands, exact resource names, or attack steps.

This branch focuses on Azure; AWS labs are a work in progress and are not yet
catalogued here.
"""

AZURE_LAB_INFO = {
    "add_sp_credentials": {
        "name": "Add Service Principal Credentials",
        "category": "Identity / Privilege Escalation",
        "summary": "An admin removed a user as owner of an app registration but forgot the underlying service principal, which holds powerful directory permissions. Lingering ownership lets the user mint new credentials and escalate.",
        "objective": "Capture the flag by leveraging leftover service principal ownership to authenticate as a privileged identity and join an admin group.",
    },
    "acr_image_secrets": {
        "name": "ACR Image Secrets -- Leaked Admin Creds to Image Layers",
        "category": "Containers / Secrets",
        "summary": "A private Azure Container Registry has its admin account enabled, and those credentials were left in a resource's tags where any Reader can find them. The image they unlock was built carelessly, with a secret embedded in a layer and only 'deleted' later — so it still ships inside the image.",
        "objective": "Use the leaked registry admin credentials to pull the image, then recover the flag that hides in a deleted image layer (the obvious runtime config is a decoy).",
    },
    "apim_named_value": {
        "name": "APIM Named Value -- Plaintext Secret Exposure",
        "category": "Credentials in Files",
        "summary": "An Azure API Management instance stores a sensitive value as a Named Value that was never marked as a secret, leaving it readable in plaintext through the management API to anyone with basic Reader access.",
        "objective": "Retrieve the flag stored as a plaintext Named Value in Azure API Management.",
    },
    "app_configuration_secrets": {
        "name": "App Configuration -- Data Reader Enumeration",
        "category": "Configuration / Secrets",
        "summary": "A central Azure App Configuration store holds application settings and secrets, but the Data Reader role granted for runtime access lets any holder enumerate every key-value pair, including credentials meant only for the app.",
        "objective": "Retrieve the flag by enumerating key-values in the App Configuration store using read access.",
    },
    "app_service_env_vars": {
        "name": "App Service Environment Variables -- Secret Exposure",
        "category": "Web / Secrets",
        "summary": "A web app on Azure App Service keeps credentials directly in its Application Settings. Any identity with config-list rights can pull every setting in plaintext through the ARM API rather than the app runtime.",
        "objective": "Retrieve the flag from the App Service application settings using management-plane access.",
    },
    "arm_deployment_history": {
        "name": "ARM Deployment History Secret Exposure",
        "category": "ARM / Credential Exposure",
        "summary": "An ARM template passed a secret as a plain string parameter instead of a secureString. Azure retains every deployment's parameter values in resource group history indefinitely, exposing the credential to anyone with Reader.",
        "objective": "Retrieve the flag from the resource group's ARM deployment history.",
    },
    "automation_account": {
        "name": "Automation Account Runbook Abuse",
        "category": "Automation / Managed Identity",
        "summary": "An Azure Automation Account has a managed identity with access to a private storage account. A user granted Automation Contributor can author runbooks that execute as that identity, indirectly reaching whatever it can.",
        "objective": "Capture the flag by running a runbook that uses the Automation Account's managed identity to read a private storage account.",
    },
    "blob_sas_abuse": {
        "name": "Blob SAS Token Exposure",
        "category": "Storage / Credential Exposure",
        "summary": "A developer hardcoded a Shared Access Signature token into client-side JavaScript served from a public web container. The token is over-scoped to the entire storage account, so any visitor who reads the source can reach private data.",
        "objective": "Retrieve the flag by using a leaked over-scoped SAS token to access a private storage container.",
    },
    "cloudshell": {
        "name": "Cloud Shell Storage Exposure",
        "category": "Storage / RBAC",
        "summary": "Azure Cloud Shell persists a user's home directory as a disk image in a file share. Weak RBAC on the storage account lets an attacker download and mount the image to extract credentials and other sensitive data.",
        "objective": "Capture the flag by downloading and mounting the Cloud Shell disk image and using the credentials it contains.",
    },
    "container_app_env_vars": {
        "name": "Container App Env Vars -- Secrets in Environment Variables",
        "category": "Containers / Secrets",
        "summary": "An Azure Container App stores a sensitive value directly in its environment variables, which are exposed in the resource definition and visible to anyone with Reader access on the resource group.",
        "objective": "Read the Container App definition to find the flag stored in an environment variable.",
    },
    "container_instance_env": {
        "name": "Container Instance -- Plaintext Environment Variables",
        "category": "Containers / Secrets",
        "summary": "An app on Azure Container Instances keeps secrets in non-secure environment variables. ACI returns these in plaintext via the ARM API, so any Reader on the resource group can read them without touching the container runtime.",
        "objective": "Retrieve the flag from the container group's plaintext environment variables.",
    },
    "data_factory_linked_service": {
        "name": "Data Factory Linked Service -- Cleartext Credentials",
        "category": "Integration / Secrets",
        "summary": "An Azure Data Factory linked service stores its connection string inline without Key Vault integration, leaving the embedded storage account key readable through the ARM API to any Reader.",
        "objective": "Read the Data Factory linked service definition to extract the cleartext storage key in the connection string.",
    },
    "deployment_script": {
        "name": "Deployment Script -- Sensitive Data in Script Outputs",
        "category": "IaC / Data Exposure",
        "summary": "An Azure Deployment Script wrote sensitive data to its outputs during provisioning. Those outputs persist in the resource definition and are readable by anyone with Reader access on the resource group.",
        "objective": "Retrieve the Deployment Script outputs to find the flag.",
    },
    "device_code_phishing": {
        "name": "Device Code Phishing",
        "category": "Identity / OAuth Phishing",
        "summary": "Microsoft's OAuth device code flow, built for input-constrained devices, can be abused by initiating the flow and socially engineering a victim into entering the code, yielding the attacker a full token pair without the victim's password.",
        "objective": "Capture the flag by phishing a victim's token via the device code flow and using it to read a private storage account.",
    },
    "dynamic_groups_abuse": {
        "name": "Dynamic Groups Abuse",
        "category": "Identity / Privilege Escalation",
        "summary": "Entra ID dynamic security groups assign membership from user attributes. An attacker with rights to edit their own account attributes can satisfy a group's rule and inherit the permissions that group holds.",
        "objective": "Capture the flag by self-assigning into a privileged dynamic group and reading its Key Vault secret.",
    },
    "eventgrid_webhook_token": {
        "name": "Event Grid -- Webhook Token Exposure via ARM",
        "category": "Integration / Secrets",
        "summary": "An Event Grid subscription authenticates its webhook by embedding a secret token in the destination URL as a query parameter. The full URL is stored in the subscription definition and returned by the ARM API to any Reader.",
        "objective": "Retrieve the flag from the webhook token embedded in the Event Grid subscription's endpoint URL.",
    },
    "exposed_app_registration": {
        "name": "Exposed App Registration Client Secret",
        "category": "Identity / Credential Exposure",
        "summary": "A developer committed an app config file containing an app registration's client ID and secret to a public blob container. The service principal behind it has access to a private storage account holding the flag.",
        "objective": "Capture the flag by extracting leaked service principal credentials from a public config blob and using them to read private storage.",
    },
    "foci": {
        "name": "Family of Client IDs (FOCI) Refresh Token Abuse",
        "category": "Identity / OAuth Token Abuse",
        "summary": "Microsoft's undocumented FOCI feature lets a refresh token for one first-party app be redeemed for tokens scoped to a different first-party app without re-consent, unlocking scopes the original app lacked.",
        "objective": "Capture the flag by exchanging a family refresh token for a new client ID to gain Graph scopes and modify group membership.",
    },
    "function_ssrf": {
        "name": "Azure Function App SSRF to Managed Identity Token",
        "category": "Serverless / SSRF / IMDS",
        "summary": "An Azure Function App exposes an HTTP endpoint that fetches arbitrary user-supplied URLs without validation. The function carries a managed identity with access to a private storage account, turning the SSRF into a credential-theft path.",
        "objective": "Capture the flag by abusing the server-side request forgery to obtain a managed identity token and read a private blob.",
    },
    "illicit_consent_grant": {
        "name": "Illicit Consent Grant",
        "category": "Identity / OAuth Phishing",
        "summary": "An attacker-controlled Azure AD application requests dangerous OAuth delegated permissions through a phishing link. When a privileged administrator consents, the attacker inherits broad access to mail, files, and role assignment capabilities.",
        "objective": "Capture the flag by tricking an administrator into granting consent and using the resulting token to access protected resources.",
    },
    "keyvault_misconfig": {
        "name": "Key Vault Misconfiguration",
        "category": "Key Vault / Access Policy",
        "summary": "An Azure Key Vault runs in legacy access-policy mode with an overly permissive policy that accidentally grants a low-privilege user read access to secrets, while public network access remains enabled.",
        "objective": "Retrieve the flag by discovering the vault and reading the secret exposed through the misconfigured access policy.",
    },
    "logic_app_credentials": {
        "name": "Logic App -- Hardcoded Credentials in Workflow Definition",
        "category": "Integration / Secrets",
        "summary": "An Azure Logic App workflow hardcodes a bearer token directly in an HTTP action header. Because the full workflow definition is readable by anyone with Reader on the resource group, the embedded secret is exposed in plaintext.",
        "objective": "Retrieve the flag by reading the Logic App workflow definition and extracting the embedded credential.",
    },
    "managed_identity_abuse": {
        "name": "Managed Identity Abuse",
        "category": "Compute / IMDS",
        "summary": "A VM has a managed identity with read access to a private storage account, and a low-privilege account holds a VM role that seems harmless but permits running arbitrary commands on the host, which exposes the identity token.",
        "objective": "Capture the flag by running commands on the VM to obtain its managed identity token and read a private blob.",
    },
    "monitor_action_group": {
        "name": "Monitor Action Group -- Webhook Token Exposure",
        "category": "Monitoring / Secrets",
        "summary": "An Azure Monitor Action Group is configured with a webhook receiver whose URL embeds an authentication token in plaintext. The token sits in the ARM resource definition where any Reader can see it.",
        "objective": "Retrieve the flag by inspecting the Action Group webhook receiver URL for the embedded token.",
    },
    "pass_the_prt": {
        "name": "Pass-the-PRT: Lateral Movement to the Cloud",
        "category": "Identity / PRT Abuse / MFA Bypass",
        "summary": "An Azure AD-joined Windows VM caches a victim user's Primary Refresh Token, a long-lived SSO credential. With local admin on the host, an attacker can extract and replay this token to authenticate to the cloud while bypassing MFA.",
        "objective": "Capture the flag by extracting the cached Primary Refresh Token, impersonating the victim, and reading a secret from Key Vault.",
    },
    "policy_assignment_metadata": {
        "name": "Policy Assignment Metadata -- Secret in Policy Metadata",
        "category": "Governance / Secrets",
        "summary": "An Azure Policy assignment stores an internal reference token in its metadata field. This metadata is unencrypted and fully visible to anyone with Reader access in scope.",
        "objective": "Retrieve the flag by reading the policy assignment metadata where the token was stored.",
    },
    "policy_privesc": {
        "name": "Azure Policy Privilege Escalation",
        "category": "Governance / Privilege Escalation",
        "summary": "A user holds a role that appears limited to managing compliance policies but grants write access to initiative definitions. An existing initiative runs with a highly privileged managed identity that can be abused via policy remediation.",
        "objective": "Capture the flag by injecting a malicious deploy policy into a privileged initiative to escalate access and read the protected storage blob.",
    },
    "resource_group_tags": {
        "name": "Resource Group Tags -- Credentials in Metadata",
        "category": "Identity / Secrets",
        "summary": "A platform team stored a service principal secret in an Azure resource group tag as an internal note. Resource tags are visible to any identity with Reader, exposing the credential to enumeration.",
        "objective": "Retrieve the flag by enumerating resource groups and reading the secret embedded in their tags.",
    },
    "sa_public_access": {
        "name": "Storage Account Public Access",
        "category": "Storage Misconfiguration",
        "summary": "A production Azure Storage account has containers configured with anonymous public access at the container and blob levels. A publicly readable config file leaks the path to a sensitive blob meant to stay hidden.",
        "objective": "Capture the flag by enumerating the public storage account, following the leaked path, and fetching the hidden blob.",
    },
    "secrets_chain": {
        "name": "Secrets Chain -- Sequential Plaintext Credential Path",
        "category": "Credential Exposure / Chained",
        "summary": "One sequential lab that consolidates the 'plaintext credentials in an Azure resource' scenarios into a single attack path. Starting from an anonymous web visitor, each leaked secret unlocks or names the next resource — a SAS token, a service principal, an App Configuration store, a Data Factory connection string, a Container Instance, and finally a Key Vault.",
        "objective": "Follow the chain of leaked plaintext credentials from the public portal all the way to the Key Vault secret that holds the flag.",
    },
    "shared_key_auth": {
        "name": "Shared Key Authorization",
        "category": "Storage / Function App / Key Vault",
        "summary": "A user was granted a storage role assumed to be management-only, but it exposes the account shared key and shared key auth was left enabled. The storage account hosts function code backed by a managed identity with Key Vault access.",
        "objective": "Capture the flag by using the shared key to tamper with function code, leak the managed identity token, and read the Key Vault secret.",
    },
    "sqli_imds": {
        "name": "SQL Injection -- IMDS Token Exfiltration",
        "category": "Compute / SQL Injection / IMDS",
        "summary": "A web app on an Azure VM builds SQL queries by concatenating raw user input, allowing injection. The VM has a managed identity with Key Vault access, so command execution via the database can be pivoted to steal the identity token.",
        "objective": "Capture the flag by exploiting the SQL injection to execute commands, retrieve the managed identity token, and read the Key Vault secret.",
    },
    "storage_account_keys": {
        "name": "Storage Account Keys -- Control Plane to Data Plane Bypass",
        "category": "Storage / Privilege Escalation",
        "summary": "An attacker account was granted a storage role assumed to be read-only metadata, but it includes the ability to list account keys. Those master keys bypass RBAC entirely and grant full access to private blob data.",
        "objective": "Retrieve the flag by listing the storage account keys and using them to download a private blob.",
    },
    "terraform_state_exposure": {
        "name": "Terraform State File Exposure",
        "category": "Storage / Secrets in State",
        "summary": "A team stores Terraform remote state in a blob container left publicly readable. Even outputs marked sensitive are written to the state file in plaintext, exposing credentials and secrets to anyone who can fetch it.",
        "objective": "Retrieve the flag by downloading the publicly accessible Terraform state file and extracting the secret output.",
    },
    "vm_extension_settings": {
        "name": "VM Extension -- Plaintext Settings in ARM",
        "category": "Compute / Secrets",
        "summary": "A Custom Script Extension on a Linux VM passes its bootstrap command through the unencrypted settings block instead of protected settings. The plaintext value is returned by the ARM API to anyone with Reader.",
        "objective": "Retrieve the flag by reading the VM extension settings exposed in plaintext through ARM.",
    },
    "vm_run_command": {
        "name": "VM RunCommand -- Arbitrary Code Execution via Contributor Role",
        "category": "Compute / Privilege Escalation",
        "summary": "An attacker holds a VM management role that seems limited to operations like resize and restart, but it also permits running arbitrary shell commands as root on the VM without SSH or credentials.",
        "objective": "Capture the flag by using the run-command capability to execute a shell command that reads the protected file on the VM.",
    },
}
