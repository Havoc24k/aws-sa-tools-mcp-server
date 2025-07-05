# AWS MCP Server

A Model Context Protocol (MCP) server that provides tools to interact with AWS services.

## Features

### AWS SDK tools

These are the main features of the AWS MCP server that you can use to interact with AWS services. If something is not listed here, it can be supported by the `aws_sdk_wrapper()` tool in `aws_mcp_server.tools`, assuming the AWS SDK supports it and that the LLM can properly create the command.

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

- **IAM Security**
  - Security compliance checks via Logicom prompts


## Prerequisites

- Python 3.12 or higher
- AWS credentials configured (`~/.aws/credentials`)
- AWS CLI profile setup

### Installation Requirements

1. Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
2. Install Python 3.10 or newer using `uv python install 3.10` (or a more recent version)

## Installation

Configure your Claude Desktop settings by adding the following to `claude_desktop_config.json`:

```json
{
    "mcpServers": {
        "aws-mcp-server": {
            "command": "uvx",
            "args": [
                "--directory",
                "/path/to/aws-mcp-server",
                ".",
            ]
        }
    }
}
```

### WSL

```json
{
    "mcpServers": {
        "aws-mcp-server": {
            "command": "wsl.exe",
            "args": [
                "bash",
                "-c",
                "uvx --directory /path/to/aws-mcp-server ."
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
