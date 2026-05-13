output "attacker_access_key_id" {
  value     = aws_iam_access_key.attacker.id
  sensitive = false
}

output "attacker_secret_access_key" {
  value     = aws_iam_access_key.attacker.secret
  sensitive = true
}

output "hosted_zone_id" {
  value = aws_route53_zone.lab.zone_id
}

output "hosted_zone_name" {
  value = aws_route53_zone.lab.name
}
