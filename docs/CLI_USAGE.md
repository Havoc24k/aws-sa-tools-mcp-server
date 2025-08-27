# CLI Usage Guide

This guide shows how to use the AWS MCP Server via command line interface for testing and development.

## Server Modes

The AWS MCP Server supports two transport modes:

### STDIO Mode (Default)
Used by Claude Desktop and MCP clients:
```bash
# Run with STDIO transport
python -m aws_mcp_server.server

# Or using uvx
uvx aws-mcp-server

# Or if installed
aws-mcp-server
```

### SSE Mode (HTTP API)
For HTTP-based testing and integration:
```bash
# Run with SSE transport 
# Server binds to 0.0.0.0:8888 (accessible via localhost:8888)
python -m aws_mcp_server.server --sse --port 8888

# With custom port
python -m aws_mcp_server.server --sse --port 8080
```

**Note**: In SSE mode, the server always binds to `0.0.0.0` (all interfaces) but you can access it via `localhost:<port>` for local testing.

## HTTP API Testing

When running in SSE mode, you can test the server using curl commands.

### Basic Setup (3 Terminal Workflow)

**Terminal 1** - Start the server:
```bash
# Default port 8888, binds to 0.0.0.0 (all interfaces)
python -m aws_mcp_server.server --sse --port 8888
```

**Terminal 2** - Monitor server responses:
```bash
# Connect via localhost (server binds to 0.0.0.0:8888)
curl -N -H 'Accept: text/event-stream' http://localhost:8888/sse
```
This will show you the session ID and all server responses.

**Terminal 3** - Send commands:

#### 1. Extract Session ID
From Terminal 2 output, copy the session ID:
```
session_id=abc123def456...
```

#### 2. Initialize Session
```bash
SESSION_ID=your_session_id_here

curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "curl-client", "version": "1.0.0"}
    }
  }' \
  "http://localhost:8888/messages/?session_id=$SESSION_ID"

curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }' \
  "http://localhost:8888/messages/?session_id=$SESSION_ID"
```

#### 3. List Available Tools
```bash
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }' \
  "http://localhost:8888/messages/?session_id=$SESSION_ID"
```

### Example Tool Calls

#### List S3 Buckets
```bash
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "s3-list_buckets",
      "arguments": {
        "profile_name": "default",
        "region": "us-east-1"
      }
    }
  }' \
  "http://localhost:8888/messages/?session_id=$SESSION_ID"
```

#### List EC2 Instances
```bash
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "ec2-describe_instances",
      "arguments": {
        "region": "us-east-1",
        "profile_name": "default"
      }
    }
  }' \
  "http://localhost:8888/messages/?session_id=$SESSION_ID"
```

#### Generic AWS SDK Call
```bash
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "aws_sdk_wrapper",
      "arguments": {
        "service_name": "iam",
        "operation_name": "list_users",
        "region_name": "us-east-1",
        "profile_name": "default",
        "operation_kwargs": {}
      }
    }
  }' \
  "http://localhost:8888/messages/?session_id=$SESSION_ID"
```

## Command Line Options

Available CLI arguments:
```bash
python -m aws_mcp_server.server [options]

Options:
  --sse                    Use SSE transport (HTTP API mode)
  --port PORT             Port to run the server on (default: 8888)
  --enable-vector-store   Enable vector store features
  --data-source PATH      Path to data source directory (default: datasource/)
  --log-file PATH         Path to log file (default: logs/aws_mcp_server.log)
```

## Environment Configuration

Set environment variables to customize server behavior:

```bash
# AWS settings
export AWS_DEFAULT_REGION=us-east-1
export AWS_PROFILE=default

# Vector store (optional)
export ENABLE_VECTOR_STORE=true
export CHROMA_DB_PATH=./chroma_db
export DATA_SOURCE_PATH=./datasource

# Logging
export AWS_MCP_DEBUG=true
```

## Testing Different AWS Profiles

You can test with different AWS profiles by changing the `profile_name` parameter:

```bash
# Test with a specific profile
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "tools/call",
    "params": {
      "name": "s3-list_buckets",
      "arguments": {
        "profile_name": "production",
        "region": "eu-west-1"
      }
    }
  }' \
  "http://localhost:8888/messages/?session_id=$SESSION_ID"
```

## Debugging

### Enable Debug Logging
```bash
export AWS_MCP_DEBUG=true
python -m aws_mcp_server.server --sse --port 8888
```

### Check Server Health
```bash
curl http://localhost:8888/sse
```

### Validate AWS Credentials
```bash
# Test AWS credentials before starting server
aws sts get-caller-identity --profile default
```

## Common Issues

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8888

# Kill the process
kill -9 <PID>
```

### AWS Credentials Not Found
```bash
# Check AWS configuration
aws configure list --profile default

# Set up credentials
aws configure --profile default
```

### Server Not Responding
- Check firewall settings
- Verify the server is running on the correct host/port
- Check server logs for errors

## Response Format

All responses follow JSON-RPC 2.0 format:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Response data here"
      }
    ]
  }
}
```

Errors are returned as:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -1,
    "message": "Error description"
  }
}
```