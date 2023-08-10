# Vulnerable Application Information
In this vulnerable scenario, the administrator exhibited a lack of attentiveness when assigning roles to individuals. 
Consequently, he allocated the "Storage Account Contributor" role with the misconception that it solely pertained to control plane management, neglecting the potential influence on the data plane. Moreover he completely forgot to disable shared key authorization.

The currently deployed storage account serves as a repository for code associated with several function apps under development by an intern. 
These function apps have the capability to be triggered through HTTP requests and have been assigned a managed identity, facilitating the retrieval of secrets from a designated key vault.

The code residing within the storage possesses the ability to manipulate the contents of the function apps, allowing for the acquisition of a managed identity token and subsequent access to the confidential "flag" secret located within the aforementioned key vault.

---

## ⚠️ Warning

**Important:** Details regarding the attack, safeguards, and methods for identifying this vulnerability, weakness, or misconfiguration are available in the PDF document.

---
