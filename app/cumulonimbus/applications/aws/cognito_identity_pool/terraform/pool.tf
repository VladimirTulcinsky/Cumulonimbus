resource "random_id" "suffix" {
  byte_length = 4
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# S3 bucket and flag object accessible only to the Cognito unauth role
resource "aws_s3_bucket" "flag" {
  bucket        = "cumulonimbus-cognito-${random_id.suffix.hex}"
  force_destroy = true
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "aws_s3_bucket_public_access_block" "flag" {
  bucket                  = aws_s3_bucket.flag.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "flag" {
  bucket  = aws_s3_bucket.flag.id
  key     = "secret/flag.txt"
  content = "CUMULONIMBUS{C0gn1t0_Un4uth_1d3nt1ty_AWS_Cr3ds}"
}

# Unauthenticated IAM role assumed by Cognito guest identities
data "aws_iam_policy_document" "cognito_unauth_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = ["cognito-identity.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "cognito-identity.amazonaws.com:aud"
      values   = [aws_cognito_identity_pool.pool.id]
    }
    condition {
      test     = "ForAnyValue:StringLike"
      variable = "cognito-identity.amazonaws.com:amr"
      values   = ["unauthenticated"]
    }
  }
}

resource "aws_iam_role" "cognito_unauth" {
  name               = "cognito-unauth-${random_id.suffix.hex}"
  assume_role_policy = data.aws_iam_policy_document.cognito_unauth_assume.json
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

data "aws_iam_policy_document" "cognito_unauth" {
  statement {
    sid    = "ReadFlag"
    effect = "Allow"
    actions = [
      "s3:GetObject",
    ]
    resources = ["${aws_s3_bucket.flag.arn}/secret/flag.txt"]
  }
}

resource "aws_iam_role_policy" "cognito_unauth" {
  name   = "read-flag-${random_id.suffix.hex}"
  role   = aws_iam_role.cognito_unauth.id
  policy = data.aws_iam_policy_document.cognito_unauth.json
}

# Identity pool allowing unauthenticated (guest) access
resource "aws_cognito_identity_pool" "pool" {
  identity_pool_name               = "cumulonimbus_${random_id.suffix.hex}"
  allow_unauthenticated_identities = true
  allow_classic_flow               = false
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "aws_cognito_identity_pool_roles_attachment" "pool" {
  identity_pool_id = aws_cognito_identity_pool.pool.id
  roles = {
    unauthenticated = aws_iam_role.cognito_unauth.arn
  }
}
