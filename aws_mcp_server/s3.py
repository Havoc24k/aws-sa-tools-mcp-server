from typing import Any
import boto3
from aws_mcp_server.mcp import mcp


@mcp.tool(
    name="s3-list_buckets",
    description="""
    Get a list of all S3 buckets in the account.

    Args:
        profile_name (str): The name of the AWS profile to use.
    """
)
async def s3_list_buckets(profile_name: str, region: str) -> dict:
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    s3 = session.client('s3', region_name=region)
    response = s3.list_buckets()
    return response


@mcp.tool(
    name="s3-list_objects",
    description="""
    Get a list of all objects in the specified S3 bucket.

    Args:
        profile_name (str): The name of the AWS profile to use.
        bucket_name (str): The name of the S3 bucket.
    """
)
async def s3_list_objects(profile_name: str, region: str, bucket_name: str) -> dict:
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    s3 = session.client('s3', region_name=region)
    response = s3.list_objects(Bucket=bucket_name)
    return response
