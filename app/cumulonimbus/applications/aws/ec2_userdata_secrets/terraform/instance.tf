resource "random_id" "ec2_userdata_secrets" {
  byte_length = 6
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_vpc" "ec2_userdata_secrets" {
  cidr_block = "10.0.0.0/16"
  tags       = { Name = "cumulonimbus-userdata-${random_id.ec2_userdata_secrets.hex}" }
}

resource "aws_subnet" "ec2_userdata_secrets" {
  vpc_id            = aws_vpc.ec2_userdata_secrets.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "eu-west-1a"
}

resource "aws_security_group" "ec2_userdata_secrets" {
  name   = "cumulonimbus-userdata-${random_id.ec2_userdata_secrets.hex}"
  vpc_id = aws_vpc.ec2_userdata_secrets.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# The victim EC2 instance — user data contains a bootstrap script with
# a hardcoded database password and the flag embedded as an env variable.
# User data is retrievable via the EC2 API without ever SSHing into the instance.
resource "aws_instance" "app_server" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.ec2_userdata_secrets.id
  vpc_security_group_ids = [aws_security_group.ec2_userdata_secrets.id]

  # Misconfiguration: secrets hardcoded in user data, readable by any IAM
  # principal with ec2:DescribeInstanceAttribute on this instance
  user_data = base64encode(<<-BASH
    #!/bin/bash
    # Cumulonimbus app-server bootstrap script
    # TODO: migrate secrets to SSM Parameter Store before next release

    export DB_HOST="db.internal.cumulonimbus.corp"
    export DB_USER="appuser"
    export DB_PASS="Sup3rS3cr3tDB2024!"
    export API_SECRET="CUMULONIMBUS{3c2_Us3rD4t4_S3cr3ts_3xp0s3d}"
    export ENVIRONMENT="production"

    yum update -y
    echo "Bootstrap complete"
  BASH
  )

  tags = { Name = "cumulonimbus-app-server-${random_id.ec2_userdata_secrets.hex}" }
}

# ── Attacker user ─────────────────────────────────────────────────────────────

resource "aws_iam_user" "attacker" {
  name = "cloud-auditor-${random_id.ec2_userdata_secrets.hex}"
}

resource "aws_iam_access_key" "attacker" {
  user = aws_iam_user.attacker.name
}

# Misconfiguration: ec2:DescribeInstances + ec2:DescribeInstanceAttribute
# are commonly included in read-only auditor policies without realising that
# DescribeInstanceAttribute with attribute=userData returns the full user data script.
resource "aws_iam_user_policy" "attacker" {
  name = "ec2-read-only"
  user = aws_iam_user.attacker.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["ec2:DescribeInstances", "ec2:DescribeInstanceAttribute"]
      Resource = "*"
    }]
  })
}
