import boto3
from aws_mcp_server.mcp import mcp


@mcp.tool(
    name="rds-describe_db_instances",
    description="""
    Get a list of all RDS instances in the account.

    Args:
        profile_name (str): The name of the AWS profile to use.
        region (str): The AWS region to use.
    """
)
async def rds_describe_db_instances(profile_name: str, region: str) -> dict:
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    rds = session.client('rds', region_name=region)
    response = rds.describe_db_instances()
    return response
