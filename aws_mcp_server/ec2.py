import boto3
from aws_mcp_server.mcp import mcp


@mcp.tool(
    name="ec2-describe_instances",
    description="""
    Get a list of all EC2 instances in the account."

    Args:
        profile_name (str): The name of the AWS profile to use.
        region (str): The AWS region to use.
    """
)
async def ec2_describe_instances(profile_name: str, region: str) -> dict:
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    ec2 = session.client('ec2', region_name=region)
    response = ec2.describe_instances()
    return response


@mcp.tool(
    name="ec2-describe_security_groups",
    description="""
    Get a list of all security groups in the account.

    Args:
        profile_name (str): The name of the AWS profile to use.
        region (str): The AWS region to use.
    """
)
async def ec2_describe_security_groups(profile_name: str, region: str) -> dict:
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    ec2 = session.client('ec2', region_name=region)
    response = ec2.describe_security_groups()
    return response


@mcp.tool(
    name="ec2-describe_vpcs",
    description="""
    Get a list of all VPCs in the account."

    Args:
        profile_name (str): The name of the AWS profile to use.
        region (str): The AWS region
    """
)
async def ec2_describe_vpcs(profile_name: str, region: str) -> dict:
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    ec2 = session.client('ec2', region_name=region)
    response = ec2.describe_vpcs()
    return response
