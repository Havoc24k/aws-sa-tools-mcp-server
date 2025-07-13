#!/bin/bash

# AWS MCP Server Deployment Script
# This script builds and deploys the MCP server to AWS App Runner

set -e

# Configuration
SERVICE_NAME="aws-mcp-server"
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_PROFILE="${AWS_PROFILE:-default}"

echo "🚀 Deploying AWS MCP Server to App Runner"
echo "Service: $SERVICE_NAME"
echo "Region: $AWS_REGION"
echo "Profile: $AWS_PROFILE"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity --profile "$AWS_PROFILE" >/dev/null 2>&1; then
    echo "❌ AWS CLI not configured or profile '$AWS_PROFILE' not found"
    exit 1
fi

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --profile "$AWS_PROFILE" --query Account --output text)
ECR_URI="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$SERVICE_NAME"

echo "📦 Building Docker image..."

# Build the Docker image
docker build -t "$SERVICE_NAME" .

# Tag for ECR
docker tag "$SERVICE_NAME:latest" "$ECR_URI:latest"

echo "🔐 Logging into ECR..."

# Login to ECR
aws ecr get-login-password --region "$AWS_REGION" --profile "$AWS_PROFILE" | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

echo "⬆️ Pushing image to ECR..."

# Create ECR repository if it doesn't exist
aws ecr describe-repositories --repository-names "$SERVICE_NAME" --region "$AWS_REGION" --profile "$AWS_PROFILE" >/dev/null 2>&1 || \
aws ecr create-repository --repository-name "$SERVICE_NAME" --region "$AWS_REGION" --profile "$AWS_PROFILE"

# Push the image
docker push "$ECR_URI:latest"

echo "🎯 Deploying with Terraform..."

# Navigate to terraform directory
cd deployment/terraform

# Initialize Terraform if needed
if [ ! -d ".terraform" ]; then
    terraform init
fi

# Plan and apply
terraform plan -var="aws_region=$AWS_REGION" -var="service_name=$SERVICE_NAME"
terraform apply -var="aws_region=$AWS_REGION" -var="service_name=$SERVICE_NAME" -auto-approve

# Get the service URL
SERVICE_URL=$(terraform output -raw service_url)

echo "✅ Deployment complete!"
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "To test the deployment:"
echo "curl $SERVICE_URL"