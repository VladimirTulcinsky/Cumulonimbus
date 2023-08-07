# Vulnerable Application Information
In this vulnerable application, a user named "norightsuser" has been created. 
At one point, this user held ownership over the "group-add-app" application. 
However, due to a job transition, his ownership was revoked from the application registration. 
Feeling discontent, he now intends to create disruption within the environment.

In a somewhat oversight, the administrator only removed norightsuser's owner status from the application registration, overlooking his presence in the service principal. Could this oversight be exploited?

This application has application permissions that enable the addition of members to groups. 
Among these groups is "cred-administrators. Since our lack of Azure AD licenses prevents us from assigning roles to groups, it is necessary to assume that the "cred-administrators" group has been granted the "Global Administrators" role. 
Consequently, if the attacker can manipulate the "group-add-app", he gains the ability to include himself in the Global Administrators group. 
This is the primary objective of this application.


## ⚠️ Warning

**Important:** Details regarding the attack, safeguards, and methods for identifying this vulnerability, weakness, or misconfiguration are available in the PDF document.

---