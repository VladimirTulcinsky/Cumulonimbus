resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "app" {
  bucket        = "cumulonimbus-acl-${random_id.suffix.hex}"
  force_destroy = true
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# BlockPublicAcls must be false to allow object-level public ACLs
resource "aws_s3_bucket_public_access_block" "app" {
  bucket = aws_s3_bucket.app.id

  block_public_acls       = false
  block_public_policy     = true
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_ownership_controls" "app" {
  bucket = aws_s3_bucket.app.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
  depends_on = [aws_s3_bucket_public_access_block.app]
}

# Decoy objects with private ACL — these look interesting but contain nothing
resource "aws_s3_object" "decoy_readme" {
  bucket = aws_s3_bucket.app.id
  key    = "internal/README.md"
  acl    = "private"
  content = "Internal documentation index. See /internal/docs/ for details."
  depends_on = [aws_s3_bucket_ownership_controls.app]
}

resource "aws_s3_object" "decoy_config" {
  bucket = aws_s3_bucket.app.id
  key    = "internal/config.json"
  acl    = "private"
  content = jsonencode({ environment = "production", region = "eu-west-1" })
  depends_on = [aws_s3_bucket_ownership_controls.app]
}

# Flag object — individual object ACL set to public-read while bucket blocks public policies
resource "aws_s3_object" "flag" {
  bucket       = aws_s3_bucket.app.id
  key          = "public/release-notes.txt"
  acl          = "public-read"
  content      = "CUMULONIMBUS{S3_0bj3ct_ACL_Publ1c_R3ad}"
  content_type = "text/plain"
  depends_on   = [aws_s3_bucket_ownership_controls.app]
}
