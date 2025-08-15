# AWS MCP Server Deployment Guide

This guide covers deploying the AWS MCP Server to AWS App Runner using Terraform.

## Quick Deploy

```bash
# Navigate to Terraform directory
cd deployment/terraform

# Initialize Terraform
terraform init

# Deploy with your AWS profile
AWS_PROFILE=your-profile terraform apply -auto-approve
```

## Prerequisites

- AWS CLI configured with appropriate permissions
- Docker installed
- Terraform installed
- AWS profile configured (default: `HEY`)

## Configuration

### Default Settings

The deployment is optimized for demo/development with cost-effective settings:

- **Region**: `eu-central-1` (configurable)
- **Service Name**: `aws-mcp-server`
- **CPU**: `0.25 vCPU` (minimum)
- **Memory**: `0.5 GB` (minimum)
- **Auto-scaling**: 1-2 instances, 10 max concurrency
- **Health Check**: `/sse` endpoint

### Environment Variables

The service runs with these environment variables:
- `AWS_DEFAULT_REGION`: `eu-central-1`
- `AWS_MCP_TRANSPORT`: `sse`
- `AWS_MCP_PORT`: `8888`

## Terraform Deployment

### 1. Navigate to Terraform Directory

```bash
cd deployment/terraform
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Deploy Infrastructure

```bash
# With specific AWS profile
AWS_PROFILE=your-profile terraform apply -auto-approve

# With default profile
terraform apply -auto-approve
```

### 4. Get Service URL

```bash
terraform output service_url
```

## What Gets Deployed

### Infrastructure

- **ECR Repository**: Container registry for Docker images
- **IAM Roles**: Service and instance roles with minimal permissions
- **App Runner Service**: Container-based web service
- **Auto-scaling Configuration**: Demo-optimized scaling (1-2 instances)

### IAM Permissions

The App Runner instance has these managed policies:
- `AmazonEC2ReadOnlyAccess`
- `AmazonS3ReadOnlyAccess`
- `AmazonRDSReadOnlyAccess`
- `CloudWatchReadOnlyAccess`

### Security

- HTTPS enabled by default
- IAM roles follow least privilege principle
- No AWS credentials stored in container
- ECR authentication handled automatically

## Container Deployment

The deployment uses container-based deployment with:
- **Base Image**: Chainguard-based multi-stage build
- **Port**: 8888 (SSE transport)
- **Health Check**: `/sse` endpoint
- **Auto-scaling**: 1-2 instances for demo cost optimization

## Testing

```bash
# Get service URL
SERVICE_URL=$(terraform output -raw service_url)

# Test health check
curl -I "https://$SERVICE_URL/sse"

# Test MCP protocol
curl -X POST -H 'Content-Type: application/json' -d '{
  "jsonrpc": "2.0", 
  "id": 1, 
  "method": "tools/list", 
  "params": {}
}' "https://$SERVICE_URL/messages/?session_id=test"
```

## Cost Optimization

### Demo Configuration (Current)
- **CPU**: 0.25 vCPU
- **Memory**: 0.5 GB
- **Scaling**: 1-2 instances max
- **Estimated Cost**: ~$5-10/month

### Production Scaling
To scale for production, update `variables.tf`:
```hcl
variable "cpu" {
  default = "1 vCPU"
}

variable "memory" {
  default = "2 GB"
}
```

## Monitoring

App Runner provides built-in monitoring:
- Application logs in CloudWatch
- CPU, memory, and request metrics
- Health check monitoring
- Auto-scaling metrics

### View Logs

```bash
# List log groups
aws logs describe-log-groups --log-group-name-prefix "/aws/apprunner"

# View recent logs
aws logs tail "/aws/apprunner/aws-mcp-server" --follow
```

## Troubleshooting

### Common Issues

1. **Terraform Apply Fails**
   - Ensure AWS profile has sufficient permissions
   - Check AWS credentials: `aws sts get-caller-identity`

2. **Service Unhealthy**
   - Check CloudWatch logs
   - Verify `/sse` endpoint responds with 200

3. **ECR Access Denied**
   - Verify IAM roles are properly configured
   - Check if ECR repository exists

### Debug Commands

```bash
# Check service status
aws apprunner describe-service --service-arn $(terraform output -raw service_arn)

# View recent logs
aws logs tail "/aws/apprunner/aws-mcp-server" --since 1h

# Test health check
curl -I "https://$(terraform output -raw service_url)/sse"
```

## Updating the Deployment

To update the service:

```bash
# Update Terraform configuration
terraform plan

# Apply changes
terraform apply -auto-approve
```

## Cleanup

To remove all resources:

```bash
terraform destroy -auto-approve
```

## Variables

Customize deployment by modifying `variables.tf`:

```hcl
variable "service_name" {
  default = "aws-mcp-server"
}

variable "aws_region" {
  default = "eu-central-1"
}

variable "cpu" {
  default = "0.25 vCPU"
}

variable "memory" {
  default = "0.5 GB"
}
```