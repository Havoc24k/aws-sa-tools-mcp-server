variable "service_name" {
  description = "Name of the MCP server service"
  type        = string
  default     = "aws-mcp-server"
}

variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "eu-central-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "cpu" {
  description = "CPU allocation for App Runner service"
  type        = string
  default     = "0.25 vCPU"
}

variable "memory" {
  description = "Memory allocation for App Runner service"
  type        = string
  default     = "0.5 GB"
}