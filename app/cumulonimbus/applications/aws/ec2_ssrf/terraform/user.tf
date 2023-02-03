# create attacker user
resource "aws_iam_user" "attacker" {
  name = "attacker"
  path = "/"
}

resource "aws_iam_access_key" "attacker" {
  user = aws_iam_user.attacker.name
}

resource "aws_iam_user_policy_attachment" "attacker" {
  user       = aws_iam_user.attacker.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}

# create user to read public recipe
resource "aws_iam_user" "public_recipy_reader" {
  name = "public_recipy_reader"
  path = "/"
}

resource "aws_iam_access_key" "public_recipy_reader" {
  user = aws_iam_user.public_recipy_reader.name
}

resource "aws_iam_user_policy" "public_recipy_reader" {
  user = aws_iam_user.public_recipy_reader.name
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ],
        Effect = "Allow",
        Resource = [
          "${aws_s3_bucket.ssrf.arn}/public_recipe.txt",
          "${aws_s3_bucket.ssrf.arn}"
        ]
      },
      {
        Action   = "s3:ListAllMyBuckets",
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}


