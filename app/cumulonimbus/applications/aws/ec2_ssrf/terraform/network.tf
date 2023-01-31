resource "aws_vpc" "ssrf" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "vpc-ssrf"
  }
}

resource "aws_subnet" "ssrf" {
  vpc_id                  = aws_vpc.ssrf.id
  cidr_block              = "10.0.0.0/24"
  map_public_ip_on_launch = true

  tags = {
    Name = "subnet-ssrf"
  }
}

resource "aws_security_group" "ssrf" {
  name        = "web"
  description = "Allow HTTP and SSH traffic"
  vpc_id      = aws_vpc.ssrf.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.attacker_public_ip]
  }
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}
