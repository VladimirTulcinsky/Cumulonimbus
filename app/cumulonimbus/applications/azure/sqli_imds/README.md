# sqli_imds — SQL Injection → IMDS Token Exfiltration

python3 -m json.tool
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
