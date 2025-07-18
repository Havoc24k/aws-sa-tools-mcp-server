terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.9"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# IAM role for App Runner service
resource "aws_iam_role" "apprunner_service_role" {
  name = "${var.service_name}-apprunner-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "build.apprunner.amazonaws.com"
        }
      }
    ]
  })
}

# IAM role for App Runner instance (for AWS API access)
resource "aws_iam_role" "apprunner_instance_role" {
  name = "${var.service_name}-apprunner-instance-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "tasks.apprunner.amazonaws.com"
        }
      }
    ]
  })
}

# Attach ECR access policy to App Runner service role
resource "aws_iam_role_policy_attachment" "apprunner_service_ecr_access" {
  role       = aws_iam_role.apprunner_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

# Attach AWS managed policies for common AWS service access
resource "aws_iam_role_policy_attachment" "apprunner_instance_ec2_readonly" {
  role       = aws_iam_role.apprunner_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "apprunner_instance_s3_readonly" {
  role       = aws_iam_role.apprunner_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "apprunner_instance_rds_readonly" {
  role       = aws_iam_role.apprunner_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonRDSReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "apprunner_instance_cloudwatch_readonly" {
  role       = aws_iam_role.apprunner_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess"
}

# ECR repository for container images
resource "aws_ecr_repository" "mcp_server" {
  name                 = var.service_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# Wait for IAM policy propagation
resource "time_sleep" "wait_for_iam_policy_propagation" {
  depends_on = [aws_iam_role_policy_attachment.apprunner_service_ecr_access]
  
  create_duration = "30s"
}

# Auto-scaling configuration for demo environment
resource "aws_apprunner_auto_scaling_configuration_version" "demo_scaling" {
  auto_scaling_configuration_name = "${var.service_name}-demo-scaling"
  min_size                       = 1
  max_size                       = 2
  max_concurrency               = 10

  tags = {
    Name        = "${var.service_name}-demo-scaling"
    Environment = var.environment
  }
}

# App Runner service
resource "aws_apprunner_service" "mcp_server" {
  service_name = var.service_name

  source_configuration {
    auto_deployments_enabled = false
    
    image_repository {
      image_identifier      = "${aws_ecr_repository.mcp_server.repository_url}:latest"
      image_configuration {
        port = "8888"
        runtime_environment_variables = {
          AWS_DEFAULT_REGION = var.aws_region
          AWS_MCP_TRANSPORT  = "sse"
          AWS_MCP_PORT       = "8888"
        }
      }
      image_repository_type = "ECR"
    }
    
    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_service_role.arn
    }
  }

  # Authentication configuration for ECR
  depends_on = [
    aws_iam_role_policy_attachment.apprunner_service_ecr_access,
    time_sleep.wait_for_iam_policy_propagation
  ]

  instance_configuration {
    cpu               = var.cpu
    memory            = var.memory
    instance_role_arn = aws_iam_role.apprunner_instance_role.arn
  }

  auto_scaling_configuration_arn = aws_apprunner_auto_scaling_configuration_version.demo_scaling.arn

  health_check_configuration {
    healthy_threshold   = 1
    interval            = 10
    path                = "/sse"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 5
  }

  tags = {
    Name        = var.service_name
    Environment = var.environment
  }
}

# Output the service URL
output "service_url" {
  value = aws_apprunner_service.mcp_server.service_url
}

output "ecr_repository_url" {
  value = aws_ecr_repository.mcp_server.repository_url
}