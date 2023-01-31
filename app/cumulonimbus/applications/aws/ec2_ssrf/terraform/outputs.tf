output "shared_credentials_files" {
  value = var.shared_credentials_files
}
output "shared_config_files" {
  value = var.shared_config_files
}
output "attacker_aws_access_key_id" {
  value = aws_iam_access_key.attacker.id
}
output "attacker_aws_secret_access_key" {
  value     = aws_iam_access_key.attacker.secret
  sensitive = true
}

