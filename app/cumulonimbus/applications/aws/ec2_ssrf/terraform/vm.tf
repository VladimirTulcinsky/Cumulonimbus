data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }

  owners = ["099720109477"] # Canonical
}

resource "aws_key_pair" "ssrf-key-pair" {
  key_name   = "ssrf-key-pair"
  public_key = file(pathexpand("~/.ssh/${var.app_id}.pub"))
}

resource "aws_instance" "ssrf" {
  ami             = data.aws_ami.ubuntu.id
  instance_type   = "t2.micro"
  subnet_id       = aws_subnet.ssrf.id
  security_groups = [aws_security_group.ssrf.id]
  user_data       = file("${path.module}/../web_app/requirements.sh")
  tags = {
    Name = "ec2-ssrf"
  }

  provisioner "file" {
    source      = "../web_app/ssrf.js"
    destination = "/home/ubuntu/ssrf.js"
  }
}

resource "aws_iam_instance_profile" "ssrf" {
  name = "ssrf"
  role = aws_iam_role.ssrf_assume_role.name
}

resource "aws_iam_role" "ssrf_assume_role" {
  name = "EC2AssumeRole"
  path = "/"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
               "Service": "ec2.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }
    ]
}
EOF
}





