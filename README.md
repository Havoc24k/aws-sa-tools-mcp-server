# AWS MCP Server

A Model Context Protocol (MCP) server that provides tools to interact with AWS services.

## Features

- **S3 Operations**
  - List buckets
  - List objects in buckets

- **EC2 Operations**
  - Describe instances
  - List security groups
  - List VPCs

- **RDS Operations**
  - Describe database instances

- **Cost Explorer**
  - Get cost and usage reports
  - Get resource-specific cost analysis

- **CloudWatch**
  - Retrieve metric statistics

- **Local File System**
  - List local folders
  - Read code files

- **Terraform**
  - Read remote state files

## Prerequisites

- Python 3.12 or higher
- AWS credentials configured (`~/.aws/credentials`)
- AWS CLI profile setup

## Installation

Configure your Claude Desktop settings by adding the following to `claude_desktop_config.json`:

```json
{
    "mcpServers": {
        "aws-api": {
            "command": "uv",
            "args": [
                "--directory",
                "/path/to/aws-mcp-server",
                "run",
                "server.py"
            ]
        }
    }
}
```

### WSL

```json
{
    "mcpServers": {
        "aws-api": {
            "command": "wsl.exe",
            "args": [
                "bash",
                "-c",
                "uv --directory /path/to/aws-mcp-server run server.py"
            ]
        }
    }
}
```

Ensure your AWS credentials are properly configured in `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```
