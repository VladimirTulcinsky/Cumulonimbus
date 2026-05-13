resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "aws_iam_user" "attacker" {
  name = "cumulonimbus-${var.app_id}-attacker-${random_string.suffix.result}"
  tags = {
    app_id = var.app_id
  }
}

resource "aws_iam_access_key" "attacker" {
  user = aws_iam_user.attacker.name
}

resource "aws_iam_user_policy" "attacker" {
  name = "route53-read"
  user = aws_iam_user.attacker.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "route53:ListHostedZones",
          "route53:ListHostedZonesByName",
          "route53:GetHostedZone",
          "route53:ListResourceRecordSets",
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_route53_zone" "lab" {
  name = "cumulonimbus-${random_string.suffix.result}.internal"

  tags = {
    app_id = var.app_id
  }
}

resource "aws_route53_record" "flag" {
  zone_id = aws_route53_zone.lab.zone_id
  name    = "flag.cumulonimbus-${random_string.suffix.result}.internal"
  type    = "TXT"
  ttl     = 300

  records = ["CUMULONIMBUS{R0ut353_TXT_R3c0rd_S3cr3ts}"]
}

resource "aws_route53_record" "decoy_a" {
  zone_id = aws_route53_zone.lab.zone_id
  name    = "app.cumulonimbus-${random_string.suffix.result}.internal"
  type    = "A"
  ttl     = 300

  records = ["10.0.0.1"]
}

resource "aws_route53_record" "decoy_cname" {
  zone_id = aws_route53_zone.lab.zone_id
  name    = "api.cumulonimbus-${random_string.suffix.result}.internal"
  type    = "CNAME"
  ttl     = 300

  records = ["app.cumulonimbus-${random_string.suffix.result}.internal"]
}
