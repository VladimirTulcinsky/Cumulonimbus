resource "random_id" "s3_public_access" {
  byte_length = 6
}

# Misconfiguration 1: Block Public Access is disabled
resource "aws_s3_bucket" "data" {
  bucket        = "cumulonimbus-data-${random_id.s3_public_access.hex}"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket = aws_s3_bucket.data.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# Misconfiguration 2: bucket policy grants anonymous GetObject
resource "aws_s3_bucket_policy" "data_public_read" {
  bucket = aws_s3_bucket.data.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.data.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.data]
}

resource "aws_s3_object" "flag" {
  bucket       = aws_s3_bucket.data.id
  key          = "flag.txt"
  content      = "CUMULONIMBUS{S3_Publ1c_Acc3ss_Bl0ck_D1sabl3d}\n"
  content_type = "text/plain"
}

# Decoy file in the same bucket
resource "aws_s3_object" "readme" {
  bucket       = aws_s3_bucket.data.id
  key          = "README.txt"
  content      = "Cumulonimbus internal data store. Contact data-team@example.com for access requests.\n"
  content_type = "text/plain"
}
