output "attacker_aws_access_key_id" {
  value = aws_iam_access_key.attacker.id
}

output "attacker_aws_secret_access_key" {
  value     = aws_iam_access_key.attacker.secret
  sensitive = true
}

output "instance_id" {
  value = aws_instance.app_server.id
}
