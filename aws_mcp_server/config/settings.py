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
# Simplified configuration - use single values for all services (KISS principle)
DEFAULT_TIMEOUT_SECONDS = int(os.getenv("AWS_MCP_TIMEOUT", "30"))
