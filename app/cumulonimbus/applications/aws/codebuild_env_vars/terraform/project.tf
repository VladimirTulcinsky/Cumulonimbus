resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "artifacts" {
  bucket        = "cumulonimbus-cb-${random_id.suffix.hex}"
  force_destroy = true
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

data "aws_iam_policy_document" "codebuild_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["codebuild.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "codebuild" {
  name               = "cumulonimbus-cb-${random_id.suffix.hex}"
  assume_role_policy = data.aws_iam_policy_document.codebuild_assume.json
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "aws_iam_role_policy_attachment" "codebuild_basic" {
  role       = aws_iam_role.codebuild.name
  policy_arn = "arn:aws:iam::aws:policy/AWSCodeBuildDeveloperAccess"
}

# CodeBuild project with plaintext environment variables — readable via codebuild:BatchGetProjects
resource "aws_codebuild_project" "app" {
  name          = "cumulonimbus-deploy-${random_id.suffix.hex}"
  description   = "Production deployment pipeline"
  service_role  = aws_iam_role.codebuild.arn
  build_timeout = 5

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/standard:7.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    # Plaintext variables — value returned by BatchGetProjects in full
    environment_variable {
      name  = "ENVIRONMENT"
      value = "production"
    }

    environment_variable {
      name  = "DATABASE_HOST"
      value = "prod-db.internal.example.com"
    }

    environment_variable {
      name  = "DATABASE_PASSWORD"
      value = "Pr0d_DB_P4ssw0rd_2024"
      type  = "PLAINTEXT"
    }

    environment_variable {
      name  = "DEPLOY_API_KEY"
      value = "CUMULONIMBUS{C0d3Bu1ld_Pl41nt3xt_Env_V4rs}"
      type  = "PLAINTEXT"
    }
  }

  source {
    type      = "NO_SOURCE"
    buildspec = <<-YAML
      version: 0.2
      phases:
        build:
          commands:
            - echo Deploying application
    YAML
  }

  logs_config {
    cloudwatch_logs {
      status = "DISABLED"
    }
  }

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# Attacker IAM user with codebuild:BatchGetProjects + codebuild:ListProjects
resource "aws_iam_user" "attacker" {
  name = "cb-reader-${random_id.suffix.hex}"
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
    sid    = "CodeBuildRead"
    effect = "Allow"
    actions = [
      "codebuild:BatchGetProjects",
      "codebuild:ListProjects",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_user_policy" "attacker" {
  name   = "cb-reader-policy-${random_id.suffix.hex}"
  user   = aws_iam_user.attacker.name
  policy = data.aws_iam_policy_document.attacker.json
}
