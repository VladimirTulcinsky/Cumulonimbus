output "attacker_access_key_id" {
  description = "Attacker IAM user access key ID"
  value       = aws_iam_access_key.attacker.id
}

output "attacker_secret_access_key" {
  description = "Attacker IAM user secret access key"
  value       = aws_iam_access_key.attacker.secret
  sensitive   = true
}

output "attacker_username" {
  description = "Attacker IAM username"
  value       = aws_iam_user.attacker.name
}

output "glue_job_name" {
  description = "Glue job name"
  value       = aws_glue_job.etl.name
}
