resource "random_id" "suffix" {
  byte_length = 4
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# VPC and networking — minimal setup for SSM endpoint reachability
resource "aws_vpc" "app" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = {
    Name    = "cumulonimbus-ssm-${random_id.suffix.hex}"
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "aws_internet_gateway" "app" {
  vpc_id = aws_vpc.app.id
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "aws_subnet" "app" {
  vpc_id                  = aws_vpc.app.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "aws_route_table" "app" {
  vpc_id = aws_vpc.app.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.app.id
  }
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "aws_route_table_association" "app" {
  subnet_id      = aws_subnet.app.id
  route_table_id = aws_route_table.app.id
}

resource "aws_security_group" "app" {
  name        = "cumulonimbus-ssm-${random_id.suffix.hex}"
  description = "SSM Session Manager lab"
  vpc_id      = aws_vpc.app.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# IAM instance profile with SSM managed instance core policy
data "aws_iam_policy_document" "ec2_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ssm_instance" {
  name               = "cumulonimbus-ssm-instance-${random_id.suffix.hex}"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume.json
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.ssm_instance.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ssm" {
  name = "cumulonimbus-ssm-${random_id.suffix.hex}"
  role = aws_iam_role.ssm_instance.name
}

resource "aws_instance" "target" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.app.id
  vpc_security_group_ids = [aws_security_group.app.id]
  iam_instance_profile   = aws_iam_instance_profile.ssm.name

  user_data = <<-BASH
    #!/bin/bash
    echo 'CUMULONIMBUS{SSM_S3ss10n_M4n4g3r_Sh3ll_4cc3ss}' > /root/flag.txt
    chmod 600 /root/flag.txt
  BASH

  tags = {
    Name    = "cumulonimbus-target-${random_id.suffix.hex}"
    app_id  = var.app_id
    managed = "terraform"
  }
}

# Attacker IAM user — ssm:StartSession + ec2:DescribeInstances (no SSH key needed)
resource "aws_iam_user" "attacker" {
  name = "ssm-attacker-${random_id.suffix.hex}"
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "aws_iam_access_key" "attacker" {
  user = aws_iam_user.attacker.name
}

data "aws_iam_policy_document" "attacker" {
  statement {
    sid    = "SSMSession"
    effect = "Allow"
    actions = [
      "ssm:StartSession",
      "ssm:DescribeSessions",
      "ssm:TerminateSession",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "DescribeInstances"
    effect = "Allow"
    actions = [
      "ec2:DescribeInstances",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_user_policy" "attacker" {
  name   = "ssm-attacker-policy-${random_id.suffix.hex}"
  user   = aws_iam_user.attacker.name
  policy = data.aws_iam_policy_document.attacker.json
}
