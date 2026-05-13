resource "random_id" "secrets_manager_enum" {
  byte_length = 6
}

# ── Secrets in AWS Secrets Manager ───────────────────────────────────────────

resource "aws_secretsmanager_secret" "flag" {
  name                    = "/cumulonimbus/production/flag-${random_id.secrets_manager_enum.hex}"
  description             = "Production flag credential"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "flag" {
  secret_id     = aws_secretsmanager_secret.flag.id
  secret_string = "CUMULONIMBUS{S3cr3ts_M4n4g3r_0v3rp3rm1ss1v3}"
}

# Decoy secrets to make enumeration more realistic
resource "aws_secretsmanager_secret" "db_password" {
  name                    = "/cumulonimbus/production/db-password-${random_id.secrets_manager_enum.hex}"
  description             = "Production database password"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = "{\"username\":\"appuser\",\"password\":\"Sup3rS3cr3tDB!\"}"
}

resource "aws_secretsmanager_secret" "api_key" {
  name                    = "/cumulonimbus/production/third-party-api-${random_id.secrets_manager_enum.hex}"
  description             = "Third-party payment API key"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "api_key" {
  secret_id     = aws_secretsmanager_secret.api_key.id
  secret_string = "sk_live_9f8a7b6c5d4e3f2a1b0c"
}

# ── Attacker user ─────────────────────────────────────────────────────────────

resource "aws_iam_user" "attacker" {
  name = "svc-monitoring-${random_id.secrets_manager_enum.hex}"
}

resource "aws_iam_access_key" "attacker" {
  user = aws_iam_user.attacker.name
}

# Misconfiguration: the policy uses Resource = "*" instead of scoping to
# specific secret ARNs. A monitoring account only needed read access to
# one secret but got access to everything.
resource "aws_iam_user_policy" "attacker" {
  name = "secrets-read-overpermissive"
  user = aws_iam_user.attacker.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "secretsmanager:ListSecrets"
        Resource = "*"
      },
      {
        # Should be scoped to a single secret ARN, not wildcard
        Effect   = "Allow"
        Action   = "secretsmanager:GetSecretValue"
        Resource = "arn:aws:secretsmanager:eu-west-1:*:secret:/cumulonimbus/*"
      }
    ]
  })
}
