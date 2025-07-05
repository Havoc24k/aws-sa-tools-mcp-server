from typing import Any
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(
    name="aws-mcp-server",
    instructions="""
    This is a FastMCP server that provides a set of tools to interact with AWS services.
    It includes tools to list S3 buckets, describe EC2 instances, get cost and usage reports,
    retrieve CloudWatch metrics, manage RDS instances, and perform IAM security checks.
    The server is designed to be used with the MCP protocol and can be run in a local environment.

    The server works under two modes, each mode has its own set of permissions and capabilities and defines the actions that can be performed on AWS resources.

    Default Mode:
        Read only actions are allowed on any AWS account. This is the default mode and it must always be applied.

    Unsafe Mode:
        This mode allows the user to execute any AWS SDK operation. This includes creating, updating, and deleting resources.
        This mode is not recommended for production use and should only be used in a controlled environment.
        Use this mode at your own risk.
        In order to enable this mode, the user must be asked twice to confirm.

    Never assume that the user wants to start with the Unsafe mode. Always start with the Default mode.
    """
)
