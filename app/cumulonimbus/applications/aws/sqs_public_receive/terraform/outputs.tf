output "queue_url" {
  description = "SQS queue URL"
  value       = aws_sqs_queue.app.url
}

output "queue_name" {
  description = "SQS queue name"
  value       = aws_sqs_queue.app.name
}
