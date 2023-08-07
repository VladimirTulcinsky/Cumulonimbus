# Device Code Phishing and Token Misuse

In this scenario, the attacker must obtain a special refresh token called a family refresh token. This kind of token can be obtained by phishing a user using the device code phish technique. This technique abuses the OAuth 2.0 device authorization grant flow.

To enable this flow, the device prompts the user to visit a webpage on another device to sign in and enter a specific code. Once the user is successfully signed in, the device obtains the necessary access tokens and refresh tokens. The attacker misuses this flow by deceiving the victim into entering the specific code and login information, allowing the attacker to receive the tokens.

In this vulnerable application, we simulate the device code phishing as it is not the most interesting part of the attack. The cyber range user runs the following command:

```
az login --use-device-code --allow-no-subscriptions
```

This grants the user a code that is used to log in to [https://microsoft.com/devicelogin](https://microsoft.com/devicelogin). Instead of the attacker tricking the victim to enter the code that is provided by Microsoft, the attacker will himself enter this code with the credentials of the victim which will be outputted in the cyber range. The tokens will be available in `msal_token_cache.json`.

The ultimate goal of this vulnerable application is to make the attacker add an account with low privileges that he has compromised to the group of global administrators by abusing the undocumented feature that gives the ability of refresh tokens to be redeemed for bearer tokens as any other client in the family.

It is important to note that in this scenario, the attacker switches the client id, but in reality, it is not necessary. The attacker can already add users to groups using the permissions of the Azure CLI. Since the purpose of this cyber range is to reduce costs, we assume that users do not have licenses. Therefore, they do not have access to the entire 365 suite, such as emails, OneDrive, or SharePoint. The Azure CLI application allows adding a user to a group but does not permit reading emails. In such cases, switching the client id to Microsoft Office application (`d3590ed6-52b3-4102-aeff-aad2292ab01c`) can be useful. The goal of this vulnerable application is solely to demonstrate the possibility of switching the client id.


## ⚠️ Warning

**Important:** Details regarding the attack, safeguards, and methods for identifying this vulnerability, weakness, or misconfiguration are available in the PDF document.

---


