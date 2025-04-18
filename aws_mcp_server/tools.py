import boto3
from typing import Any
from aws_mcp_server.mcp import mcp


@mcp.resource("resource://aws_config")
def get_aws_config() -> dict:
    """
    Get the AWS configuration from the user's home directory.

    Returns:
        dict: The AWS configuration.
    """
    # Get a list of all AWS profiles from the user's home directory ~/.aws/config
    config = boto3.Session().available_profiles
    return config


@mcp.tool(
    name="aws_sdk_wrapper",
    description="""
    A generic AWS SDK wrapper to call any AWS service and operation.

    Args:
        service_name (str): The name of the AWS service to call (e.g. 's3', 'ec2', 'rds', etc.).
        operation_name (str): The name of the operation to call (e.g. 'list_buckets', 'describe_instances', etc.).
        region_name (str): The AWS region to use.
        profile_name (str): The name of the AWS profile to use.
        operation_kwargs (dict): The arguments to pass to the operation.
    Returns:
        Any: The response from the AWS service.
    Example:
        aws_sdk_wrapper('ce', 'get_cost_and_usage_with_resources', region_name='us-east-1', profile_name='my_profile', operation_kwargs={'TimePeriod': {'Start': '2023-01-01', 'End': '2023-01-31'}, 'Granularity': 'MONTHLY', 'GroupBy': [{'Type': 'DIMENSION', 'Key': 'SERVICE'}], 'Metrics': ['BlendedCost']})
    """
)
async def aws_sdk_wrapper(
    service_name: str,
    operation_name: str,
    region_name: str,
    profile_name: str,
    operation_kwargs: dict[str, Any],
) -> Any:
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    client = session.client(service_name, region_name=region_name)
    method = getattr(client, operation_name)
    response = method(**operation_kwargs)
    return response
