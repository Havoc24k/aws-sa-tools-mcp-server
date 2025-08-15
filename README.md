# AWS MCP Server

A Model Context Protocol (MCP) server that provides tools to interact with AWS services through Claude Desktop.

## Features

- **S3**: List buckets, list objects
- **EC2**: Describe instances, security groups, VPCs  
- **RDS**: Describe database instances
- **Cost Explorer**: Get cost and usage reports
- **CloudWatch**: Retrieve metric statistics
- **Generic AWS SDK**: Access any AWS operation via `aws_sdk_wrapper`
- **Vector Store**: Optional document ingestion and search capabilities

## Quick Start

### Prerequisites
- Python 3.12+
- AWS credentials configured (`~/.aws/credentials`)
- Claude Desktop installed

### Installation

1. **Install the package:**
   ```bash
   pip install aws-mcp-server
   ```

2. **Configure Claude Desktop:**
   Add to your `claude_desktop_config.json`:
   ```json
   {
       "mcpServers": {
           "aws-mcp-server": {
               "command": "aws-mcp-server"
           }
       }
   }
   ```

3. **Configure AWS credentials:**
   ```bash
   aws configure
   # OR manually edit ~/.aws/credentials:
   ```
   ```ini
   [default]
   aws_access_key_id = YOUR_ACCESS_KEY
   aws_secret_access_key = YOUR_SECRET_KEY
   region = us-east-1
   ```

## Development

### Local Development Setup
```bash
# Clone and install
git clone <repository-url>
cd aws-mcp-server
uv sync

# Run locally
uvx .
```

### Configuration Options
Set environment variables for customization:
```bash
export AWS_MCP_PORT=8888
export AWS_MCP_DEBUG=true
export ENABLE_VECTOR_STORE=true
```

## Documentation

- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment with AWS App Runner
- [Vector Store Guide](docs/VECTOR_STORE.md) - Document ingestion and search setup
- [Workflow Guide](docs/WORKFLOW.md) - Development workflows and patterns

## License

MIT License - see LICENSE file for details.
