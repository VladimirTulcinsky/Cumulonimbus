resource "aws_iam_user" "attacker" {
  name = "s3-enum-${random_id.s3_public_access.hex}"
  path = "/"
}

resource "aws_iam_access_key" "attacker" {
  user = aws_iam_user.attacker.name
}

# Minimal permissions: list all buckets, nothing else in IAM
resource "aws_iam_user_policy" "attacker" {
  name = "s3-list-only"
  user = aws_iam_user.attacker.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "s3:ListAllMyBuckets"
        Resource = "*"
      }
    ]
  })
}
