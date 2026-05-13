output "attacker_aws_access_key_id" {
  value = aws_iam_access_key.attacker.id
}

output "attacker_aws_secret_access_key" {
  value     = aws_iam_access_key.attacker.secret
  sensitive = true
}

output "parameter_path_prefix" {
  value = "/cumulonimbus/production/"
}
