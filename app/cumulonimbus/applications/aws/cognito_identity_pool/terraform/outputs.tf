output "identity_pool_id" {
  description = "Cognito Identity Pool ID"
  value       = aws_cognito_identity_pool.pool.id
}

output "flag_bucket" {
  description = "S3 bucket containing the flag"
  value       = aws_s3_bucket.flag.bucket
}

output "flag_object_key" {
  description = "S3 object key for the flag"
  value       = aws_s3_object.flag.key
}

output "account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "region" {
  description = "AWS region"
  value       = data.aws_region.current.name
}
