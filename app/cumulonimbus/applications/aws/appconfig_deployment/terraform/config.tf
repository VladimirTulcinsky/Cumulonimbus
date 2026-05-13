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
  name = "appconfig-read"
  user = aws_iam_user.attacker.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "appconfig:ListApplications",
          "appconfig:GetApplication",
          "appconfig:ListConfigurationProfiles",
          "appconfig:GetConfigurationProfile",
          "appconfig:ListHostedConfigurationVersions",
          "appconfig:GetHostedConfigurationVersion",
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_appconfig_application" "lab" {
  name        = "cumulonimbus-${var.app_id}-${random_string.suffix.result}"
  description = "Platform configuration store"

  tags = {
    app_id = var.app_id
  }
}

resource "aws_appconfig_configuration_profile" "lab" {
  application_id = aws_appconfig_application.lab.id
  name           = "platform-config"
  description    = "Core platform settings"
  location_uri   = "hosted"

  tags = {
    app_id = var.app_id
  }
}

resource "aws_appconfig_hosted_configuration_version" "lab" {
  application_id           = aws_appconfig_application.lab.id
  configuration_profile_id = aws_appconfig_configuration_profile.lab.configuration_profile_id
  content_type             = "application/json"

  content = jsonencode({
    database = {
      host     = "db.cumulonimbus.internal"
      port     = 5432
      username = "app_user"
      password = "CUMULONIMBUS{AppC0nf1g_H0st3d_C0nf1g_3xp0s3d}"
    }
    feature_flags = {
      dark_mode = true
      beta      = false
    }
    api = {
      endpoint = "https://api.cumulonimbus.internal/v2"
      timeout  = 30
    }
  })
}
