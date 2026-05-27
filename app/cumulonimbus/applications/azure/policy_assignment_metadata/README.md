# Policy Assignment Metadata — Secret in Policy Metadata

**Provider**: Azure  
**Difficulty**: Beginner  
**MITRE ATT&CK**: [T1552.001 — Credentials in Files](https://attack.mitre.org/techniques/T1552/001/)

## Scenario

You have obtained credentials for an Azure service principal with Reader access on a resource group. The resource group has an Azure Policy assignment where the platform team stored an internal reference token in the assignment's metadata field. This metadata is stored unencrypted and is fully visible to any Reader.

## Objective

Read the policy assignment metadata to find the flag embedded by the platform team.

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
2. List policy assignments scoped to the resource group:
   ```bash
   az policy assignment list \
     --resource-group <resource-group> \
     --query "[].{name:name, displayName:displayName, metadata:metadata}"
   ```
3. The `internal-token` key in the metadata contains the flag.

   Alternatively, show a specific assignment:
   ```bash
   az policy assignment show \
     --name <assignment-name> \
     --resource-group <resource-group> \
     --query metadata
   ```

## Flag

`CUMULONIMBUS{P0l1cy_M3t4d4t4_S3cr3t_3xp0s3d}`

## Remediation

- Never store secrets, tokens, or credentials in Azure Policy assignment metadata — it is plaintext and accessible to all Readers in scope.
- The metadata field is intended for categorization tags (e.g., `category`, `version`) only.
- Conduct a subscription-wide audit: `az policy assignment list --query "[?metadata]" -o table` to identify assignments with populated metadata fields.
- Store internal reference tokens in Azure Key Vault and reference them via managed identity at runtime.

## MITRE ATT&CK Mapping

| Technique ID | Technique Name | Tactic |
|---|---|---|
| [T1552](https://attack.mitre.org/techniques/T1552/) | Unsecured Credentials | Credential Access |
| [T1083](https://attack.mitre.org/techniques/T1083/) | File and Directory Discovery | Discovery |
