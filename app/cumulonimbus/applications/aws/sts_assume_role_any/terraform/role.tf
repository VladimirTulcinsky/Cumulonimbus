resource "random_id" "suffix" {
  byte_length = 4
}

# Misconfigured role: trust policy allows any AWS principal to assume it
resource "aws_iam_role" "target" {
  name = "cumulonimbus-app-role-${random_id.suffix.hex}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { AWS = "*" }
        Action    = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "aws_ssm_parameter" "flag" {
  name  = "/cumulonimbus/${var.app_id}/flag"
  type  = "SecureString"
  value = "CUMULONIMBUS{STS_Assum3_R0l3_W1ldcard_Pr1ncipal}"

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

data "aws_iam_policy_document" "target_role" {
  statement {
    sid    = "ReadFlag"
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
    ]
    resources = [aws_ssm_parameter.flag.arn]
  }
  statement {
    sid    = "DecryptFlag"
    effect = "Allow"
    actions = [
      "kms:Decrypt",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "target_role" {
  name   = "read-flag-${random_id.suffix.hex}"
  role   = aws_iam_role.target.id
  policy = data.aws_iam_policy_document.target_role.json
}

# Attacker has only iam:ListRoles + sts:AssumeRole
resource "aws_iam_user" "attacker" {
  name = "sts-attacker-${random_id.suffix.hex}"
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "aws_iam_access_key" "attacker" {
  user = aws_iam_user.attacker.name
}

data "aws_iam_policy_document" "attacker" {
  statement {
    sid    = "ListRoles"
    effect = "Allow"
    actions = [
      "iam:ListRoles",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "AssumeAny"
    effect = "Allow"
    actions = [
      "sts:AssumeRole",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_user_policy" "attacker" {
  name   = "sts-attacker-policy-${random_id.suffix.hex}"
  user   = aws_iam_user.attacker.name
  policy = data.aws_iam_policy_document.attacker.json
}
