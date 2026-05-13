resource "random_id" "suffix" {
  byte_length = 4
}

locals {
  function_name = "cumulonimbus-app-${random_id.suffix.hex}"
}

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_exec" {
  name               = "lambda-exec-${random_id.suffix.hex}"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Inline function code — no S3 bucket or build step required
data "archive_file" "handler" {
  type        = "zip"
  output_path = "${path.module}/handler.zip"

  source {
    content  = <<-PYTHON
      import json

      def handler(event, context):
          return {
              "statusCode": 200,
              "headers": {"Content-Type": "application/json"},
              "body": json.dumps({
                  "message": "Internal diagnostics endpoint",
                  "flag": "CUMULONIMBUS{L4mbd4_Funct10n_URL_N0_Auth}"
              })
          }
    PYTHON
    filename = "handler.py"
  }
}

resource "aws_lambda_function" "app" {
  function_name    = local.function_name
  role             = aws_iam_role.lambda_exec.arn
  handler          = "handler.handler"
  runtime          = "python3.11"
  filename         = data.archive_file.handler.output_path
  source_code_hash = data.archive_file.handler.output_base64sha256

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# Function URL with no authentication — publicly accessible
resource "aws_lambda_function_url" "app" {
  function_name      = aws_lambda_function.app.function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["*"]
    allow_methods = ["GET"]
  }
}
