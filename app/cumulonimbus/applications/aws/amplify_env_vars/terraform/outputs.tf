output "attacker_access_key_id" {
  value     = aws_iam_access_key.attacker.id
  sensitive = false
}

output "attacker_secret_access_key" {
  value     = aws_iam_access_key.attacker.secret
  sensitive = true
}

output "amplify_app_id" {
  value = aws_amplify_app.lab.id
}

output "amplify_app_name" {
  value = aws_amplify_app.lab.name
}
