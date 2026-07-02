resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
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
  name = "ecs-exec-access"
  user = aws_iam_user.attacker.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:ListClusters",
          "ecs:DescribeClusters",
          "ecs:ListTasks",
          "ecs:DescribeTasks",
          "ecs:DescribeTaskDefinition",
          "ecs:ExecuteCommand",
          "ssmmessages:CreateControlChannel",
          "ssmmessages:CreateDataChannel",
          "ssmmessages:OpenControlChannel",
          "ssmmessages:OpenDataChannel",
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role" "task_execution" {
  name = "cumulonimbus-${var.app_id}-exec-role-${random_string.suffix.result}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "ecs-tasks.amazonaws.com" }
        Action    = "sts:AssumeRole"
      }
    ]
  })

  tags = { app_id = var.app_id }
}

resource "aws_iam_role_policy_attachment" "task_execution" {
  role       = aws_iam_role.task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "task" {
  name = "cumulonimbus-${var.app_id}-task-role-${random_string.suffix.result}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "ecs-tasks.amazonaws.com" }
        Action    = "sts:AssumeRole"
      }
    ]
  })

  tags = { app_id = var.app_id }
}

resource "aws_iam_role_policy" "task_ssmmessages" {
  name = "ssmmessages"
  role = aws_iam_role.task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssmmessages:CreateControlChannel",
          "ssmmessages:CreateDataChannel",
          "ssmmessages:OpenControlChannel",
          "ssmmessages:OpenDataChannel",
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_security_group" "ecs_task" {
  name        = "cumulonimbus-${var.app_id}-${random_string.suffix.result}"
  description = "ECS task security group for ${var.app_id}"
  vpc_id      = data.aws_vpc.default.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { app_id = var.app_id }
}

resource "aws_ecs_cluster" "lab" {
  name = "cumulonimbus-${var.app_id}-${random_string.suffix.result}"

  configuration {
    execute_command_configuration {
      logging = "NONE"
    }
  }

  tags = { app_id = var.app_id }
}

resource "aws_ecs_task_definition" "lab" {
  family                   = "cumulonimbus-${var.app_id}-${random_string.suffix.result}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.task_execution.arn
  task_role_arn            = aws_iam_role.task.arn

  container_definitions = jsonencode([
    {
      name      = "app"
      image     = "public.ecr.aws/docker/library/alpine:3.18"
      essential = true
      command   = ["/bin/sh", "-c", "echo 'CUMULONIMBUS{ECS_3x3c_C0nt41n3r_Sh3ll}' > /flag.txt && sleep 86400"]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/cumulonimbus-${var.app_id}-${random_string.suffix.result}"
          "awslogs-region"        = "eu-west-1"
          "awslogs-stream-prefix" = "ecs"
          "awslogs-create-group"  = "true"
        }
      }
    }
  ])

  tags = { app_id = var.app_id }
}

resource "aws_ecs_service" "lab" {
  name                   = "cumulonimbus-${var.app_id}-${random_string.suffix.result}"
  cluster                = aws_ecs_cluster.lab.id
  task_definition        = aws_ecs_task_definition.lab.arn
  desired_count          = 1
  launch_type            = "FARGATE"
  enable_execute_command = true

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs_task.id]
    assign_public_ip = true
  }

  tags = { app_id = var.app_id }
}
