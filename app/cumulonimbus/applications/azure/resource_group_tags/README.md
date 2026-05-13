# Resource Group Tags — Credentials in Metadata

**Difficulty:** Beginner | **Provider:** Azure | **Category:** Identity / Secrets

## Scenario

A platform team tagged an Azure resource group with the service principal secret
"for convenience" — intending it only as an internal note. Azure resource tags
are **visible to any identity with Reader** on the resource (or subscription).

Any Reader can enumerate all resource groups in the subscription and inspect
their tags via `az group list` or the ARM API.

## Attack Path

```
[Attacker] Azure AD user (Reader on subscription)
    |
    v
az group list  -->  find cumulonimbus resource group
    |
    v
az group show --name <rg>  -->  tags JSON
    |
    v
tags["service-principal-secret"]  -->  flag
```

### Step 1 — Login as the attacker

```bash
az login --username <attacker_upn> --password <attacker_password>
```

### Step 2 — List resource groups

```bash
az group list \
  --query "[?contains(name, 'cumulonimbus')].{Name:name,Location:location}" \
  --output table
```

### Step 3 — Read the tags

```bash
RESOURCE_GROUP="<resource_group_name>"

az group show \
  --name "${RESOURCE_GROUP}" \
  --query "tags" \
  --output json
```

The `service-principal-secret` tag contains the flag.

### Alternative — enumerate all RG tags across the subscription

```bash
az group list --query "[*].{Name:name,Tags:tags}" --output json | \
  jq '.[] | select(.Tags != null) | {name: .Name, tags: .Tags}'
```

## How to Fix in Production

1. **Never store secrets in resource tags** — tags are metadata, not a secrets
   store. They are visible to every Reader on the resource.
2. **Use Azure Key Vault** for all secrets — reference them by ARN/URI in your
   deployment scripts rather than embedding values anywhere.
3. **Audit tags across your subscription** for sensitive patterns:
   ```bash
   az resource list --query "[*].tags" -o json | \
     jq '.[] | to_entries[] | select(.key | test("(?i)(pass|secret|key|token|cred)"))'
   ```
4. **Apply Azure Policy** to deny tags with key names matching sensitive patterns
   (e.g. `*secret*`, `*password*`, `*key*`).

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | T1552.001 |
| Cloud Infrastructure Discovery | T1580 |
| Valid Accounts: Cloud Accounts | T1078.004 |
