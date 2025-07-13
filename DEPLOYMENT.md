# AWS MCP Server Deployment Guide

This guide covers deploying the AWS MCP Server to AWS App Runner in SSE mode.

## Quick Deploy

```bash
# Run the automated deployment script
./deploy/scripts/deploy.sh
```

## Manual Deployment Steps

### Prerequisites

- AWS CLI configured with appropriate permissions
- Docker installed
- Terraform installed (optional, for infrastructure as code)

### 1. Build and Push Container

```bash
# Set your configuration
export AWS_REGION=us-east-1
export AWS_PROFILE=default
export SERVICE_NAME=aws-mcp-server

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$SERVICE_NAME"

# Build image
docker build -t $SERVICE_NAME .

# Create ECR repository
aws ecr create-repository --repository-name $SERVICE_NAME --region $AWS_REGION

# Login and push
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
docker tag $SERVICE_NAME:latest $ECR_URI:latest
docker push $ECR_URI:latest
```

### 2. Deploy with Terraform

```bash
cd deploy/terraform
terraform init
terraform apply -var="aws_region=$AWS_REGION" -var="service_name=$SERVICE_NAME"
```

### 3. Deploy via AWS Console

1. Go to App Runner in AWS Console
2. Create new service
3. Source: Container registry
4. Select your ECR repository
5. Configure:
   - Port: 8888
   - Environment variables:
     - `AWS_DEFAULT_REGION`: us-east-1
     - `AWS_MCP_TRANSPORT`: sse
     - `AWS_MCP_PORT`: 8888
6. Instance role: Select the created IAM role
7. Deploy

## Configuration

### Environment Variables

- `AWS_DEFAULT_REGION`: AWS region for API calls
- `AWS_MCP_TRANSPORT`: Set to "sse" for Server-Sent Events
- `AWS_MCP_PORT`: Port for the server (8888)

### IAM Permissions

The App Runner instance needs these managed policies:
- `AmazonEC2ReadOnlyAccess`
- `AmazonS3ReadOnlyAccess`
- `AmazonRDSReadOnlyAccess`
- `CloudWatchReadOnlyAccess`

For unsafe mode operations, additional permissions required.

## Testing

```bash
# Test the deployed service
curl https://your-apprunner-url.region.awsapprunner.com/

# Test SSE endpoint
curl -H "Accept: text/event-stream" https://your-apprunner-url.region.awsapprunner.com/sse
```

## Cost Optimization

- **Development**: 0.25 vCPU, 0.5 GB RAM (~$5-10/month)
- **Production**: 1 vCPU, 2 GB RAM (~$20-30/month)

App Runner charges for:
- Active container time
- Provisioned container capacity
- Request handling

## Monitoring

App Runner provides built-in monitoring:
- Application logs in CloudWatch
- Metrics for CPU, memory, requests
- Health check monitoring

## Troubleshooting

### Common Issues

1. **Container fails to start**
   - Check logs in CloudWatch
   - Verify Dockerfile builds locally

2. **AWS API access denied**
   - Verify IAM role permissions
   - Check AWS credentials configuration

3. **SSE connections failing**
   - Ensure port 8888 is properly configured
   - Check health check endpoint

### Logs

View logs in CloudWatch:
```bash
aws logs describe-log-groups --log-group-name-prefix "/aws/apprunner"
```

## Security

- App Runner provides HTTPS by default
- IAM roles follow least privilege principle
- No AWS credentials stored in container
- VPC connectivity available if needed

## Scaling

App Runner auto-scales based on:
- Request volume
- CPU utilization
- Memory usage

Configure scaling in the service settings:
- Min instances: 1
- Max instances: 10 (adjust based on needs)