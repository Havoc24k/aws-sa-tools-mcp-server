from aws_mcp.mcp import mcp
from aws_mcp import (
    ce,
    cloudwatch,
    ec2,
    filesystem,
    rds,
    s3,
    terraform,
    tools
)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
