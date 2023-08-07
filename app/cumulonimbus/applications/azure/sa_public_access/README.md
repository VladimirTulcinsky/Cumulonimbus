# Vulnerable Application Information

In this vulnerable application, two storage accounts have been created: one for the development environment and one for the production environment. Due to the requirement for globally unique storage account names, both accounts have been appended with a unique ID. While both storage accounts allow public access, access is restricted based on the attacker's public IP for security reasons. The development storage account hosts a public static website, indicating the removal of the production website due to issues.

Organizations often employ various deployment environments, such as:
- Development (DEV)
- Testing (TST)
- User Acceptance Testing (UAT)
- Performance Testing (PTP)
- Production (PRD)

Since the storage account names end with "dev," an attacker might attempt to identify storage accounts associated with other environment acronyms, such as "prd."

The second storage account contains two containers:
1. The "website" container has a public access level set to "container."
2. The "secrets" container has a public access level set to "blob."

This means that the contents of the first container can be enumerated, while the contents of the second container cannot be accessed without providing the specific container and blob names.

Using open source tools (listed below), it is possible to list public storage accounts and their containers. This enables attackers to identify files within the "website" container, including a configuration file containing variables like the URL to the "secrets" container. Additionally, a NodeJS file appends the container URL with the blob's name, "flag.txt." Armed with this information, attackers can gain access to the "hidden" blob.

## Offensive Tools:

For offensive scenarios, the following open source tools can be employed:

- [cloud_enum](https://github.com/initstring/cloud_enum)
- [BlobHunter](https://github.com/cyberark/BlobHunter)
- [Az-Blob-Attacker](https://github.com/VitthalS/Az-Blob-Attacker)
- [Microburst](https://github.com/NetSPI/MicroBurst)
- [basicblobfinder](https://github.com/joswr1ght/basicblobfinder)


## ⚠️ Warning

**Important:** Details regarding the attack, safeguards, and methods for identifying this vulnerability, weakness, or misconfiguration are available in the PDF document.

---