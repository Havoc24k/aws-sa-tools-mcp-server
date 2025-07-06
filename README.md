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

- **Vector Store & Document Management** *(Optional)*
  - PDF document ingestion with semantic search
  - Flexible categorization and metadata management
  - Support for various document types (technical, business, educational, legal, research)
  - Local ChromaDB storage with no external dependencies

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

The server uses environment variables for configuration. All settings have sensible defaults but can be customized via environment variables (see CLAUDE.md for full configuration options).

## CLI Usage

### Basic Server Commands

```bash
# Run with STDIO transport (default)
python -m aws_mcp_server.server

# Run with SSE transport
python -m aws_mcp_server.server --sse --port 8888

# Enable vector store with automatic document ingestion
python -m aws_mcp_server.server --enable-vector-store

# Specify custom data source directory
python -m aws_mcp_server.server --enable-vector-store --data-source /path/to/documents

# Combined: SSE transport with vector store
python -m aws_mcp_server.server --sse --port 8888 --enable-vector-store
```

### CLI Parameters

- `--sse` - Use Server-Sent Events transport instead of STDIO
- `--port PORT` - Port for SSE transport (default: 8888)
- `--enable-vector-store` - Enable vector store and document management features (default: disabled)
- `--data-source PATH` - Path to data source directory for automatic ingestion (default: datasource/)

### Vector Store Features

When `--enable-vector-store` is enabled:

#### Automatic Document Ingestion
- **Scans** the data source directory (default: `datasource/`) on startup
- **Ingests** all PDF files automatically with intelligent categorization
- **Tracks** file changes and only processes new/modified files
- **Maintains** an index to avoid duplicate processing

#### Additional MCP Tools
- PDF document ingestion from URLs or local files  
- Semantic search across all ingested documents
- Document categorization and metadata management
- Support for different document types with optimized presets

#### Workflow
1. **Add PDF files** to `datasource/` directory (or custom path)
2. **Start server** with `--enable-vector-store`
3. **Files are automatically ingested** and indexed
4. **Query documents** via MCP tools for semantic search

See `VECTOR_STORE.md` for detailed documentation on vector store features.

## API Examples with curl

When running with SSE transport (`--sse`), you can interact with the server using standard HTTP requests. Here are working examples:

### 1. Get Session ID

```bash
SESSION_ID=$(timeout 3 curl -N -H 'Accept: text/event-stream' http://localhost:8888/sse 2>/dev/null | grep 'session_id=' | grep -o 'session_id=[a-f0-9]*' | cut -d'=' -f2)
echo "Session ID: $SESSION_ID"
```

### 2. Initialize MCP Session

```bash
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "curl-client",
        "version": "1.0.0"
      }
    }
  }' \
  "http://localhost:8888/messages/?session_id=$SESSION_ID"
```

### 3. Search Vector Store (when enabled)

```bash
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "document_search",
      "arguments": {
        "query": "AWS security best practices encryption",
        "n_results": 2
      }
    }
  }' \
  "http://localhost:8888/messages/?session_id=$SESSION_ID"
```

### 4. Get Vector Store Information

```bash
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "vector_store_info",
      "arguments": {}
    }
  }' \
  "http://localhost:8888/messages/?session_id=$SESSION_ID"
```

### 5. AWS Service Examples

```bash
# List S3 buckets
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "s3_list_buckets",
      "arguments": {
        "region_name": "us-east-1",
        "profile_name": "default"
      }
    }
  }' \
  "http://localhost:8888/messages/?session_id=$SESSION_ID"

# Describe EC2 instances
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "ec2_describe_instances",
      "arguments": {
        "region_name": "us-east-1",
        "profile_name": "default"
      }
    }
  }' \
  "http://localhost:8888/messages/?session_id=$SESSION_ID"
```

### Important Notes

- **Responses**: All requests return 'Accepted' status - actual responses come via the SSE stream
- **Monitoring**: To see responses, run `curl -N http://localhost:8888/sse` in another terminal
- **Session**: Each request needs the same `session_id` from step 1
- **Protocol**: Uses JSON-RPC 2.0 over FastMCP SSE transport
