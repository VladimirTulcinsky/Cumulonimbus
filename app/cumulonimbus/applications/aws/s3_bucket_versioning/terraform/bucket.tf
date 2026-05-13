resource "random_id" "s3_bucket_versioning" {
  byte_length = 6
}

resource "aws_s3_bucket" "configs" {
  bucket        = "cumulonimbus-configs-${random_id.s3_bucket_versioning.hex}"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "configs" {
  bucket = aws_s3_bucket.configs.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "configs" {
  bucket                  = aws_s3_bucket.configs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Version 1 of config.json — contains the flag (simulates a secret that was
# "deleted" after being accidentally committed)
resource "aws_s3_object" "config_v1" {
  bucket       = aws_s3_bucket.configs.id
  key          = "app/config.json"
  content_type = "application/json"
  content = jsonencode({
    environment   = "production"
    database_url  = "postgresql://appuser:hunter2@db.prod.internal:5432/app"
    secret_key    = "CUMULONIMBUS{S3_V3rs10n1ng_D3l3t3d_0bj3cts}"
    debug         = false
  })

  depends_on = [aws_s3_bucket_versioning.configs]
}

# Version 2 — the "sanitised" replacement committed after the accidental exposure.
# The original version still exists in the version history.
resource "aws_s3_object" "config_v2" {
  bucket       = aws_s3_bucket.configs.id
  key          = "app/config.json"
  content_type = "application/json"
  content = jsonencode({
    environment  = "production"
    database_url = "USE_SSM_PARAMETER_STORE"
    secret_key   = "USE_SECRETS_MANAGER"
    debug        = false
  })

  depends_on = [aws_s3_object.config_v1]
}

# Delete marker — a developer ran 'aws s3 rm' thinking it would erase the history
resource "aws_s3_object" "config_deleted" {
  bucket  = aws_s3_bucket.configs.id
  key     = "app/config.json"
  content = ""

  depends_on = [aws_s3_object.config_v2]
}

# ── Attacker user ─────────────────────────────────────────────────────────────

resource "aws_iam_user" "attacker" {
  name = "s3-reader-${random_id.s3_bucket_versioning.hex}"
}

resource "aws_iam_access_key" "attacker" {
  user = aws_iam_user.attacker.name
}

resource "aws_iam_user_policy" "attacker" {
  name = "s3-versioned-read"
  user = aws_iam_user.attacker.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:ListBucket",
        "s3:ListBucketVersions",
      ]
      Resource = [
        aws_s3_bucket.configs.arn,
        "${aws_s3_bucket.configs.arn}/*",
      ]
    }]
  })
}
