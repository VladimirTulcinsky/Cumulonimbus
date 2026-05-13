output "function_url" {
  description = "Lambda function URL (publicly accessible, no auth)"
  value       = aws_lambda_function_url.app.function_url
}

output "function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.app.function_name
}
