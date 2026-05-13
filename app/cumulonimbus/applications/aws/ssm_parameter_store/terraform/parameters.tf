resource "random_id" "ssm_parameter_store" {
  byte_length = 6
}

data "aws_caller_identity" "current" {}

# ── Parameters in SSM Parameter Store ────────────────────────────────────────

resource "aws_ssm_parameter" "flag" {
  name        = "/cumulonimbus/production/flag"
  description = "Production flag credential"
  type        = "SecureString"
  value       = "CUMULONIMBUS{SSM_P4r4m3t3r_P4th_W1ldcard}"
}

# Realistic decoy parameters
resource "aws_ssm_parameter" "db_password" {
  name        = "/cumulonimbus/production/database/password"
  description = "RDS master password"
  type        = "SecureString"
  value       = "RdsMasterP@ssw0rd2024!"
}

resource "aws_ssm_parameter" "api_key" {
  name        = "/cumulonimbus/production/integrations/payment-api-key"
  description = "Payment gateway API key"
  type        = "SecureString"
  value       = "PAYMENT_KEY_cmlnmbs_51AbCdEfGhIjKlMnOpQrStUvWx"
}

resource "aws_ssm_parameter" "app_config" {
  name  = "/cumulonimbus/production/app/config"
  type  = "String"
  value = "{\"log_level\":\"info\",\"feature_flags\":{\"new_ui\":true}}"
}

# ── Attacker user ─────────────────────────────────────────────────────────────

resource "aws_iam_user" "attacker" {
  name = "deploy-agent-${random_id.ssm_parameter_store.hex}"
}

resource "aws_iam_access_key" "attacker" {
  user = aws_iam_user.attacker.name
}

# Misconfiguration: path-level wildcard grants access to ALL parameters
# under /cumulonimbus/, when the deployer only needed /cumulonimbus/production/app/*.
# Also: ssm:DescribeParameters on * lets the attacker enumerate every parameter name.
resource "aws_iam_user_policy" "attacker" {
  name = "ssm-deploy-access"
  user = aws_iam_user.attacker.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "ssm:DescribeParameters"
        Resource = "*"
      },
      {
        # Should be /cumulonimbus/production/app/* — wildcard gives too much
        Effect = "Allow"
        Action = [
          "ssm:GetParametersByPath",
          "ssm:GetParameter",
          "ssm:GetParameters",
        ]
        Resource = "arn:aws:ssm:eu-west-1:${data.aws_caller_identity.current.account_id}:parameter/cumulonimbus/*"
      },
      {
        Effect   = "Allow"
        Action   = "kms:Decrypt"
        Resource = "*"
      }
    ]
  })
}
