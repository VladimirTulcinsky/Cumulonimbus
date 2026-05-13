resource "random_id" "lambda_env_secrets" {
  byte_length = 6
}

# Lambda execution role (minimal)
resource "aws_iam_role" "lambda_exec" {
  name = "cumulonimbus-lambda-exec-${random_id.lambda_env_secrets.hex}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Minimal function code — the flag lives in the environment variable, not the code
data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = "${path.module}/lambda.zip"

  source {
    filename = "index.py"
    content  = <<-PY
      import os

      def handler(event, context):
          return {"statusCode": 200, "body": "Hello from Cumulonimbus!"}
    PY
  }
}

# Misconfiguration: API key hardcoded as an environment variable.
# Anyone with lambda:GetFunction can retrieve it via the function configuration.
resource "aws_lambda_function" "api_processor" {
  function_name    = "cumulonimbus-api-processor-${random_id.lambda_env_secrets.hex}"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "index.handler"
  runtime          = "python3.9"
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      # Misconfiguration: the flag is stored as a plaintext environment variable
      SECRET_API_KEY  = "CUMULONIMBUS{L4mbd4_3nv_S3cr3ts_Pl41nt3xt}"
      DATABASE_URL    = "postgresql://appuser:hunter2@db.internal:5432/production"
      ENVIRONMENT     = "production"
    }
  }
}

# ── Attacker user ─────────────────────────────────────────────────────────────

resource "aws_iam_user" "attacker" {
  name = "auditor-${random_id.lambda_env_secrets.hex}"
}

resource "aws_iam_access_key" "attacker" {
  user = aws_iam_user.attacker.name
}

# Misconfiguration: lambda:GetFunction is often granted as part of read-only
# "auditor" policies but it exposes plaintext environment variables including secrets.
resource "aws_iam_user_policy" "attacker" {
  name = "lambda-auditor"
  user = aws_iam_user.attacker.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["lambda:GetFunction", "lambda:ListFunctions", "lambda:GetFunctionConfiguration"]
      Resource = "*"
    }]
  })
}
