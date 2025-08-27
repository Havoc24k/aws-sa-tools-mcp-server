# AWS MCP Server Remote Client

Remote client for connecting to AWS MCP Server using FastMCP's HTTP/SSE transport.

## Prerequisites

Start the AWS MCP Server with SSE transport:
```bash
uv run python -m aws_mcp_server.server --sse --port 8888
```

## Usage

```bash
# Interactive mode (default)
python client/mcp_json_rpc_client.py

# List available tools
python client/mcp_json_rpc_client.py --action list_tools

# Test S3 tools
python client/mcp_json_rpc_client.py --action test_s3 --profile prod --region us-west-2

# Test all AWS tools
python client/mcp_json_rpc_client.py --action test_all

# Connect to remote server
python client/mcp_json_rpc_client.py --host 10.0.1.100 --port 9999
```

## Options

```text
--host HOST       Server host (default: localhost)
--port PORT       Server port (default: 8888)
--action ACTION   list_tools, test_s3, test_ec2, test_all, interactive
--profile PROFILE AWS profile (default: default)
--region REGION   AWS region (default: us-east-1)
--verbose         Enable verbose logging
```

## Interactive Mode

```text
mcp> help
mcp> list_tools
mcp> call s3-list_buckets {"profile_name": "default", "region": "us-east-1"}
mcp> call ec2-describe_instances {"profile_name": "default", "region": "us-east-1"}
mcp> quit
```

## Features

- ✅ **Remote Connection**: Connects to running MCP servers via HTTP/SSE
- ✅ **Dynamic Tool Discovery**: Automatically discovers and lists all available MCP tools
- ✅ **Interactive Mode**: Full command-line interface with tool calling
- ✅ **Multiple Actions**: List, test, and execute AWS operations remotely
- ✅ **Error Handling**: Graceful handling of connection and AWS credential issues

## Architecture

Uses FastMCP's Client class to connect to the server's SSE endpoint (`/sse`), enabling proper JSON-RPC communication over HTTP with Server-Sent Events for real-time responses.
