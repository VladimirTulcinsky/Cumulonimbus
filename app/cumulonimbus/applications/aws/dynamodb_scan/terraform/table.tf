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
  name = "dynamodb-read"
  user = aws_iam_user.attacker.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:ListTables",
          "dynamodb:DescribeTable",
          "dynamodb:Scan",
          "dynamodb:GetItem",
          "dynamodb:Query",
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_dynamodb_table" "lab" {
  name           = "cumulonimbus-${var.app_id}-${random_string.suffix.result}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "record_id"

  attribute {
    name = "record_id"
    type = "S"
  }

  tags = {
    app_id = var.app_id
  }
}

resource "aws_dynamodb_table_item" "flag" {
  table_name = aws_dynamodb_table.lab.name
  hash_key   = aws_dynamodb_table.lab.hash_key

  item = jsonencode({
    record_id   = { S = "flag" }
    description = { S = "internal-api-key" }
    value       = { S = "CUMULONIMBUS{Dyn4m0DB_Sc4n_D4t4_3xp0sur3}" }
    created_by  = { S = "platform-team" }
  })
}

resource "aws_dynamodb_table_item" "decoy_a" {
  table_name = aws_dynamodb_table.lab.name
  hash_key   = aws_dynamodb_table.lab.hash_key

  item = jsonencode({
    record_id   = { S = "config-001" }
    description = { S = "app-config" }
    value       = { S = "region=eu-west-1;timeout=30" }
    created_by  = { S = "devops-team" }
  })
}

resource "aws_dynamodb_table_item" "decoy_b" {
  table_name = aws_dynamodb_table.lab.name
  hash_key   = aws_dynamodb_table.lab.hash_key

  item = jsonencode({
    record_id   = { S = "config-002" }
    description = { S = "feature-flags" }
    value       = { S = "dark_mode=true;beta=false" }
    created_by  = { S = "devops-team" }
  })
}
