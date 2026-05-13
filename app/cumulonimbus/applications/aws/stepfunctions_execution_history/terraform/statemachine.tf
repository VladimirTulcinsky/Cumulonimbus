resource "random_id" "suffix" {
  byte_length = 4
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

data "aws_iam_policy_document" "sfn_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["states.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "sfn" {
  name               = "cumulonimbus-sfn-${random_id.suffix.hex}"
  assume_role_policy = data.aws_iam_policy_document.sfn_assume.json
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# State machine — a simple Pass state that forwards its input to the output
resource "aws_sfn_state_machine" "app" {
  name     = "cumulonimbus-workflow-${random_id.suffix.hex}"
  role_arn = aws_iam_role.sfn.arn

  definition = jsonencode({
    Comment = "Production order processing workflow"
    StartAt = "ProcessOrder"
    States = {
      ProcessOrder = {
        Type = "Pass"
        End  = true
      }
    }
  })

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# Seed one execution with sensitive input — stored in execution history indefinitely
resource "null_resource" "seed_execution" {
  provisioner "local-exec" {
    command = <<-CMD
      aws stepfunctions start-execution \
        --state-machine-arn "${aws_sfn_state_machine.app.id}" \
        --name "order-20240315-001" \
        --input '{"orderId":"ORD-20240315-001","customer":"acme-corp","payment":{"method":"card","token":"pay_cmlnmbs_abc123def456"},"internalApiKey":"CUMULONIMBUS{St3pFunct10ns_3x3cut10n_H1st0ry_L34k}"}' \
        --profile cumulonimbus \
        --region eu-west-1
    CMD
  }

  depends_on = [aws_sfn_state_machine.app]
}

# Attacker IAM user — can list and inspect executions but not run new ones
resource "aws_iam_user" "attacker" {
  name = "sfn-reader-${random_id.suffix.hex}"
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
    sid    = "SFNRead"
    effect = "Allow"
    actions = [
      "states:ListStateMachines",
      "states:DescribeStateMachine",
      "states:ListExecutions",
      "states:DescribeExecution",
      "states:GetExecutionHistory",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_user_policy" "attacker" {
  name   = "sfn-reader-policy-${random_id.suffix.hex}"
  user   = aws_iam_user.attacker.name
  policy = data.aws_iam_policy_document.attacker.json
}
