output "bucket_name" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.app.bucket
}

output "flag_object_url" {
  description = "Public URL of the flag object"
  value       = "https://${aws_s3_bucket.app.bucket}.s3.eu-west-1.amazonaws.com/${aws_s3_object.flag.key}"
}
