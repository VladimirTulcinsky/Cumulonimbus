output "attacker_access_key_id" {
  description = "Attacker IAM user access key ID"
  value       = aws_iam_access_key.attacker.id
}

output "attacker_secret_access_key" {
  description = "Attacker IAM user secret access key"
  value       = aws_iam_access_key.attacker.secret
  sensitive   = true
}

output "stack_name" {
  description = "CloudFormation stack name"
  value       = aws_cloudformation_stack.app.name
}

output "attacker_username" {
  description = "Attacker IAM username"
  value       = aws_iam_user.attacker.name
}
