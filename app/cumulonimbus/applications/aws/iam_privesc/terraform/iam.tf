data "aws_caller_identity" "current" {}

resource "random_id" "iam_privesc" {
  byte_length = 6
}

# ── Flag bucket (private, only readable via the privileged Lambda role) ────────

resource "aws_s3_bucket" "flag" {
  bucket        = "cumulonimbus-privesc-${random_id.iam_privesc.hex}"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "flag" {
  bucket                  = aws_s3_bucket.flag.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "flag" {
  bucket       = aws_s3_bucket.flag.id
  key          = "flag.txt"
  content      = "CUMULONIMBUS{1AM_Pass_R0l3_L4mbda_Pr1v3sc}\n"
  content_type = "text/plain"
}

# ── High-privilege Lambda execution role ──────────────────────────────────────
# Misconfiguration: this role grants S3 read on the flag bucket.
# Any principal with iam:PassRole + lambda:CreateFunction + lambda:InvokeFunction
# can abuse it to read the flag without being directly granted S3 access.

resource "aws_iam_role" "lambda_privileged" {
  name = "cumulonimbus-privesc-lambda-${random_id.iam_privesc.hex}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "lambda_s3_flag" {
  name = "read-flag"
  role = aws_iam_role.lambda_privileged.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:ListBucket"]
        Resource = [aws_s3_bucket.flag.arn, "${aws_s3_bucket.flag.arn}/*"]
      },
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# ── Attacker IAM user ─────────────────────────────────────────────────────────
# Misconfiguration: iam:PassRole is scoped to the privileged role,
# combined with lambda:* this is a well-known privilege escalation vector.

resource "aws_iam_user" "attacker" {
  name = "dev-${random_id.iam_privesc.hex}"
  path = "/"
}

resource "aws_iam_access_key" "attacker" {
  user = aws_iam_user.attacker.name
}

resource "aws_iam_user_policy" "attacker" {
  name = "developer-permissions"
  user = aws_iam_user.attacker.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # Allows passing the privileged Lambda role — the escalation primitive
        Effect   = "Allow"
        Action   = "iam:PassRole"
        Resource = aws_iam_role.lambda_privileged.arn
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:CreateFunction",
          "lambda:InvokeFunction",
          "lambda:GetFunction",
          "lambda:ListFunctions",
        ]
        Resource = "*"
      },
      {
        # Allows the attacker to discover the role ARN and bucket name
        Effect   = "Allow"
        Action   = ["iam:ListRoles", "s3:ListAllMyBuckets"]
        Resource = "*"
      }
    ]
  })
}
