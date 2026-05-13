output "attacker_aws_access_key_id" {
  value = aws_iam_access_key.attacker.id
}

output "attacker_aws_secret_access_key" {
  value     = aws_iam_access_key.attacker.secret
  sensitive = true
}

output "lambda_role_arn" {
  value = aws_iam_role.lambda_privileged.arn
}

output "flag_bucket_name" {
  value = aws_s3_bucket.flag.id
}
