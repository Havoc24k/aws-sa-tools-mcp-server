"""Configuration settings for AWS MCP server."""

import os

# Server settings
DEFAULT_PORT = int(os.getenv("AWS_MCP_PORT", "8888"))
DEFAULT_TRANSPORT = os.getenv("AWS_MCP_TRANSPORT", "stdio")
DEBUG = os.getenv("AWS_MCP_DEBUG", "false").lower() == "true"

# AWS specific settings
DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
DEFAULT_PROFILE = os.getenv("AWS_PROFILE", "default")

# Performance settings
MAX_CONCURRENT_REQUESTS = int(os.getenv("AWS_MCP_MAX_CONCURRENT", "10"))
ENABLE_PAGINATION = os.getenv("AWS_MCP_ENABLE_PAGINATION", "true").lower() == "true"

# AWS service limits and defaults
DEFAULT_MAX_RESULTS = int(os.getenv("AWS_MCP_MAX_RESULTS", "1000"))
DEFAULT_TIMEOUT = int(os.getenv("AWS_MCP_TIMEOUT", "30"))

# Service-specific limits (with fallback to default)
EC2_INSTANCES_MAX = int(
    os.getenv("AWS_MCP_EC2_INSTANCES_MAX", str(DEFAULT_MAX_RESULTS))
)
EC2_SECURITY_GROUPS_MAX = int(
    os.getenv("AWS_MCP_EC2_SECURITY_GROUPS_MAX", str(DEFAULT_MAX_RESULTS))
)
EC2_VPCS_MAX = int(os.getenv("AWS_MCP_EC2_VPCS_MAX", str(DEFAULT_MAX_RESULTS)))
RDS_INSTANCES_MAX = int(os.getenv("AWS_MCP_RDS_INSTANCES_MAX", "100"))
S3_OBJECTS_MAX = int(os.getenv("AWS_MCP_S3_OBJECTS_MAX", str(DEFAULT_MAX_RESULTS)))

# Timeout settings (in seconds)
AWS_API_CALL_TIMEOUT = int(os.getenv("AWS_MCP_API_TIMEOUT", str(DEFAULT_TIMEOUT)))
PAGINATION_TIMEOUT = int(os.getenv("AWS_MCP_PAGINATION_TIMEOUT", "300"))
