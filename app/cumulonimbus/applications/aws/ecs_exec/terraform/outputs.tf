output "attacker_access_key_id" {
  value     = aws_iam_access_key.attacker.id
  sensitive = false
}

output "attacker_secret_access_key" {
  value     = aws_iam_access_key.attacker.secret
  sensitive = true
}

output "cluster_name" {
  value = aws_ecs_cluster.lab.name
}

output "cluster_arn" {
  value = aws_ecs_cluster.lab.arn
}

output "service_name" {
  value = aws_ecs_service.lab.name
}
