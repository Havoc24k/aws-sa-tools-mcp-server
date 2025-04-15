from typing import Any
import boto3
from aws_mcp.mcp import mcp


@mcp.tool(
    name="read-terraform-remote-state",
    description="""
    Read the Terraform remote state from an S3 bucket.

    Args:
        profile_name (str): The name of the AWS profile to use.
        region (str): The AWS region to use.
        bucket (str): The name of the S3 bucket containing the Terraform remote state.
    """
)
async def read_terraform_remote_state(profile_name: str, region: str, bucket: str) -> dict:
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    s3 = session.client('s3', region_name=region)
    response = s3.get_object(Bucket=bucket, Key='terraform.tfstate')
    return response['Body'].read().decode('utf-8')
