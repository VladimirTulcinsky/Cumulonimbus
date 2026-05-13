output "attacker_access_key_id" {
  value     = aws_iam_access_key.attacker.id
  sensitive = false
}

output "attacker_secret_access_key" {
  value     = aws_iam_access_key.attacker.secret
  sensitive = true
}

output "application_id" {
  value = aws_appconfig_application.lab.id
}

output "application_name" {
  value = aws_appconfig_application.lab.name
}

output "configuration_profile_id" {
  value = aws_appconfig_configuration_profile.lab.configuration_profile_id
}
