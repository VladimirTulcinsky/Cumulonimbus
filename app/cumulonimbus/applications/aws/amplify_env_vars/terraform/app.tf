resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "aws_iam_user" "attacker" {
  name = "cumulonimbus-${var.app_id}-attacker-${random_string.suffix.result}"
  tags = {
    app_id = var.app_id
  }
}

resource "aws_iam_access_key" "attacker" {
  user = aws_iam_user.attacker.name
}

resource "aws_iam_user_policy" "attacker" {
  name = "amplify-read"
  user = aws_iam_user.attacker.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "amplify:ListApps",
          "amplify:GetApp",
          "amplify:ListBranches",
          "amplify:GetBranch",
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_amplify_app" "lab" {
  name = "cumulonimbus-${var.app_id}-${random_string.suffix.result}"

  environment_variables = {
    APP_ENV      = "production"
    API_ENDPOINT = "https://api.cumulonimbus.internal/v2"
    DB_HOST      = "db.cumulonimbus.internal"
    SECRET_FLAG  = "CUMULONIMBUS{4mpl1fy_App_3nv_V4rs_3xp0s3d}"
  }

  tags = {
    app_id = var.app_id
  }
}
