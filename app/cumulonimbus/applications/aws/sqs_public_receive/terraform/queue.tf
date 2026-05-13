resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_sqs_queue" "app" {
  name                       = "cumulonimbus-app-${random_id.suffix.hex}"
  message_retention_seconds  = 86400
  visibility_timeout_seconds = 30

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# Resource policy allows any AWS principal (or unauthenticated caller) to receive messages
data "aws_iam_policy_document" "public_receive" {
  statement {
    sid    = "PublicReceive"
    effect = "Allow"
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    actions   = ["sqs:ReceiveMessage"]
    resources = [aws_sqs_queue.app.arn]
  }
}

resource "aws_sqs_queue_policy" "app" {
  queue_url = aws_sqs_queue.app.id
  policy    = data.aws_iam_policy_document.public_receive.json
}

# Seed the queue with a message containing the flag using local-exec
resource "null_resource" "seed_message" {
  provisioner "local-exec" {
    command = <<-CMD
      aws sqs send-message \
        --queue-url "${aws_sqs_queue.app.url}" \
        --message-body "CUMULONIMBUS{SQS_Publ1c_R3s0urc3_P0l1cy_R3c31v3}" \
        --profile cumulonimbus \
        --region eu-west-1
    CMD
  }

  depends_on = [aws_sqs_queue_policy.app]
}
