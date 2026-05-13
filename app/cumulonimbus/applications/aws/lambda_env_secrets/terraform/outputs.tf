output "attacker_aws_access_key_id" {
  value = aws_iam_access_key.attacker.id
}

output "attacker_aws_secret_access_key" {
  value     = aws_iam_access_key.attacker.secret
  sensitive = true
}

output "function_name" {
  value = aws_lambda_function.api_processor.function_name
}
