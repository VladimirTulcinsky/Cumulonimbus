resource "random_id" "suffix" {
  byte_length = 4
}

locals {
  stack_name = "cumulonimbus-app-${random_id.suffix.hex}"
}

resource "aws_cloudformation_stack" "app" {
  name = local.stack_name

  template_body = jsonencode({
    AWSTemplateFormatVersion = "2010-09-09"
    Description              = "Cumulonimbus application stack"

    Parameters = {
      Environment = {
        Type    = "String"
        Default = "production"
      }
    }

    Resources = {
      DummyWaitHandle = {
        Type       = "AWS::CloudFormation::WaitConditionHandle"
        Properties = {}
      }
    }

    Outputs = {
      DatabasePassword = {
        Description = "RDS master password"
        Value       = "Sup3rS3cr3t!DBPass"
      }
      ApiKey = {
        Description = "Internal API key"
        Value       = "CUMULONIMBUS{Cl0udF0rm4t10n_Outputs_Expos3_S3cr3ts}"
      }
      Environment = {
        Description = "Deployment environment"
        Value       = { Ref = "Environment" }
      }
    }
  })

  tags = {
    Name    = local.stack_name
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "aws_iam_user" "attacker" {
  name = "cf-reader-${random_id.suffix.hex}"
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
    sid    = "CloudFormationDescribe"
    effect = "Allow"
    actions = [
      "cloudformation:DescribeStacks",
      "cloudformation:ListStacks",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_user_policy" "attacker" {
  name   = "cf-reader-policy-${random_id.suffix.hex}"
  user   = aws_iam_user.attacker.name
  policy = data.aws_iam_policy_document.attacker.json
}
