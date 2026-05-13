output "attacker_access_key_id" {
  value     = aws_iam_access_key.attacker.id
  sensitive = false
}

output "attacker_secret_access_key" {
  value     = aws_iam_access_key.attacker.secret
  sensitive = true
}

output "stream_name" {
  value = aws_kinesis_stream.lab.name
}

output "stream_arn" {
  value = aws_kinesis_stream.lab.arn
}
