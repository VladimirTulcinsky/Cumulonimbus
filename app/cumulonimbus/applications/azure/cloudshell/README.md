# Vulnerable Application Information

In this vulnerable application, a storage account has been created in Azure. Within this storage account, there exists a file share with a folder named `.cloudconsole` containing an `.img` file. This `.img` file is used for persistence when utilizing the cloud shell and represents a disk image of a user’s `$HOME` directory, preserving the contents within that directory. The disk image is specifically named `acc_<username>.img` and can be accessed at `fileshare.storage.windows.net/fileshare/.cloudconsole/acc_<username>.img`. It automatically synchronizes any changes made to it.

## Security Concerns

The primary concern with this setup is the lack of sufficient Role-Based Access Control (RBAC) at the storage account level. As a result, any user with access to the storage account can download the contents of the file share. This creates a security vulnerability, as the downloaded image can be mounted, and its contents, including sensitive information like passwords, tokens, command history, and error logs, can be retrieved.

## Potential Risks

A potential risk arises when an attacker combines various pieces of information obtained from the vulnerable storage account. By piecing together these details, the hacker can gain access to an administrator’s virtual machine where they will find the flag.

---

## ⚠️ Warning

**Important:** The `.img` file deployed in Azure through the vulnerable application differs from the typical Azure-created images, which are usually around 5GB in size. In this case, the image has been intentionally sanitized and optimized, resulting in a smaller size of approximately 2MB. This adjustment was made to facilitate easy inclusion of the image in the repository.

---

## ⚠️ Warning

**Important:** Details regarding the attack, safeguards, and methods for identifying this vulnerability, weakness, or misconfiguration are available in the PDF document.

---
