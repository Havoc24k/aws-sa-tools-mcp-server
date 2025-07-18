# AWS MCP Server

A Model Context Protocol (MCP) server that provides tools to interact with AWS services.

## Features

- **S3**: List buckets, list objects
- **EC2**: Describe instances, security groups, VPCs
- **RDS**: Describe database instances
- **Cost Explorer**: Get cost and usage reports
- **CloudWatch**: Retrieve metric statistics
- **Generic AWS SDK**: Access any AWS operation via `aws_sdk_wrapper`

## Prerequisites

- Python 3.12+
- AWS credentials configured (`~/.aws/credentials`)

## Installation

Configure Claude Desktop by adding to `claude_desktop_config.json`:

```json
{
    "mcpServers": {
        "aws-mcp-server": {
            "command": "uvx",
            "args": ["--directory", "/path/to/aws-mcp-server", "."]
        }
    }
}
```

Ensure AWS credentials are configured:

```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

## CLI Usage

```bash
# Run with STDIO transport (default)
python -m aws_mcp_server.server

# Run with SSE transport for HTTP API
python -m aws_mcp_server.server --sse --port 8888
```

## HTTP API Usage

When running with `--sse`, you can use curl to interact with the server:

### Setup (3 terminals)

**Terminal 1** - Start server:

```bash
python -m aws_mcp_server.server --sse --port 8888
```

**Terminal 2** - Monitor responses:

```bash
curl -N -H 'Accept: text/event-stream' https://9dytmhc5tm.eu-central-1.awsapprunner.com/sse
```

**Terminal 3** - Send commands:

```bash
# Set session ID from Terminal 2 output
SESSION_ID=your_session_id_from_terminal_2

# Initialize session
curl -X POST -H 'Content-Type: application/json' -d '{
  "jsonrpc": "2.0", "id": 1, "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05", "capabilities": {},
    "clientInfo": {"name": "curl-client", "version": "1.0.0"}
  }
}' "https://9dytmhc5tm.eu-central-1.awsapprunner.com/messages/?session_id=$SESSION_ID"

curl -X POST -H 'Content-Type: application/json' -d '{
  "jsonrpc": "2.0", "method": "notifications/initialized"
}' "https://9dytmhc5tm.eu-central-1.awsapprunner.com/messages/?session_id=$SESSION_ID"

# List tools
curl -X POST -H 'Content-Type: application/json' -d '{
  "jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}
}' "https://9dytmhc5tm.eu-central-1.awsapprunner.com/messages/?session_id=$SESSION_ID"

# List S3 buckets
curl -X POST -H 'Content-Type: application/json' -d '{
  "jsonrpc": "2.0", "id": 3, "method": "tools/call",
  "params": {
    "name": "s3-list_buckets",
    "arguments": {"profile_name": "default", "region": "us-east-1"}
  }
}' "https://9dytmhc5tm.eu-central-1.awsapprunner.com/messages/?session_id=$SESSION_ID"
```

All responses appear in Terminal 2 as JSON-RPC 2.0 formatted data.
