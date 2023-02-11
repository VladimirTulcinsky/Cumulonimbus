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
  public_key = file("./../../../../.data/.ssh/${var.app_id}.pub")
}

resource "aws_instance" "ssrf" {
  ami                  = data.aws_ami.ubuntu.id
  instance_type        = "t2.micro"
  subnet_id            = aws_subnet.ssrf.id
  security_groups      = [aws_security_group.ssrf.id]
  key_name             = aws_key_pair.ssrf-key-pair.key_name
  user_data            = <<-EOF
                        #!/bin/bash
                        echo "AWS_ACCESS_KEY=${aws_iam_access_key.public_recipy_reader.id}" 
                        echo "AWS_SECRET_KEY=${aws_iam_access_key.public_recipy_reader.secret}" 
                        ${file("${path.module}/../web_app/requirements.sh")}
                        EOF
  iam_instance_profile = aws_iam_instance_profile.ssrf.name
  tags = {
    Name = "ec2-ssrf"
  }

  provisioner "file" {
    source      = "../web_app/ssrf.js"
    destination = "/home/ubuntu/ssrf.js"
    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("./../../../../.data/.ssh/${var.app_id}")
      host        = self.public_ip
    }
  }
}

# Can't manage to set owner to ubuntu:ubuntu due to race condition
# data "cloudinit_config" "ssrf" {
#   part {
#     content_type = "text/cloud-config"
#     content = yamlencode({
#       write_files = [
#         {
#           encoding    = "b64"
#           content     = filebase64("${path.module}/../web_app/ssrf.js")
#           path        = "/home/ubuntu/ssrf.js"
#           owner       = "ubuntu:ubuntu"
#           permissions = "0111"
#         },
#         {
#           encoding    = "b64"
#           content     = filebase64("${path.module}/../web_app/requirements.sh")
#           path        = "/home/ubuntu/requirements.sh"
#           owner       = "ubuntu:ubuntu"
#           permissions = "0111"
#         },
#         {
#           content_type = "text/x-shellscript"
#           content      = <<EOT
# #!/bin/bash

# chmod +x /home/ubuntu/requirements.sh
# /home/ubuntu/requirements.sh
# EOT
#           path         = "/home/ubuntu/run_requirements.sh"
#           owner        = "ubuntu:ubuntu"
#           permissions  = "0111"
#         }
#       ]
#     })
#   }
# }

resource "aws_iam_instance_profile" "ssrf" {
  name = "ssrf"
  role = aws_iam_role.ssrf.name
}

resource "aws_iam_role" "ssrf" {
  name = "EC2AssumeRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "private_recipy_reader" {
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ],
        Effect = "Allow",
        Resource = [
          "${aws_s3_bucket.ssrf.arn}/secret_ingredient.txt",
          "${aws_s3_bucket.ssrf.arn}"
        ]
      },
      {
        Action   = "s3:ListAllMyBuckets",
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "ssrf" {
  name       = "s3_policy_attachment"
  policy_arn = aws_iam_policy.private_recipy_reader.arn
  roles      = [aws_iam_role.ssrf.name]
}
