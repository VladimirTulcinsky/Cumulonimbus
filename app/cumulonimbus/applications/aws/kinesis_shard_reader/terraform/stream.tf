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
  name = "kinesis-read"
  user = aws_iam_user.attacker.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kinesis:ListStreams",
          "kinesis:DescribeStream",
          "kinesis:DescribeStreamSummary",
          "kinesis:GetShardIterator",
          "kinesis:GetRecords",
          "kinesis:ListShards",
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_kinesis_stream" "lab" {
  name             = "cumulonimbus-${var.app_id}-${random_string.suffix.result}"
  shard_count      = 1
  retention_period = 24

  tags = {
    app_id = var.app_id
  }
}

resource "null_resource" "seed_record" {
  depends_on = [aws_kinesis_stream.lab]

  provisioner "local-exec" {
    command = <<-EOT
      aws kinesis put-record \
        --stream-name "${aws_kinesis_stream.lab.name}" \
        --partition-key "flag" \
        --data "$(echo -n 'CUMULONIMBUS{K1n3s1s_Sh4rd_R3c0rd_L34k}' | base64)" \
        --region eu-west-1 \
        --profile cumulonimbus
    EOT
  }
}
