import boto3
from . import mcp


@mcp.tool(
    name="ce-get_cost_and_usage",
    description="""
    Get the monthly cost of the AWS account.

    Args:
        profile_name (str): The name of the AWS profile to use.
        region (str): The AWS region to use.
        group_by (str): The dimension to group the costs by (e.g. 'SERVICE', 'AZ', 'REGION', 'INSTANCE_TYPE', etc.).
        start (str): The start date for the cost report in YYYY-MM-DD format.
        end (str): The end date for the cost report in YYYY-MM-DD format.
    """
)
async def ce_get_cost_and_usage(profile_name: str, region: str, group_by: str, start: str, end: str) -> dict:
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    ce = session.client('ce', region_name=region)
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start,
            'End':  end
        },
        Granularity='MONTHLY',
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': group_by
            }
        ],
        Metrics=['BlendedCost']
    )
    return response


@mcp.tool(
    name="ce-get_cost_and_usage-with-resources",
    description="""
    Get the monthly cost of the AWS account with resources.

    Args:
        profile_name (str): The name of the AWS profile to use.
        region (str): The AWS region to use.
        group_by (str): The dimension to group the costs by (e.g. 'SERVICE', 'AZ', 'REGION', 'INSTANCE_TYPE', etc.).
        start (str): The start date for the cost report in YYYY-MM-DD format.
        end (str): The end date for the cost report in YYYY-MM-DD format.
    """
)
async def ce_get_cost_and_usage_with_resources(profile_name: str, region: str, group_by: str, start: str, end: str) -> dict:
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    ce = session.client('ce', region_name=region)
    response = ce.get_cost_and_usage_with_resources(
        TimePeriod={
            'Start': start,
            'End':  end
        },
        Granularity='MONTHLY',
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': group_by
            }
        ],
        Metrics=['BlendedCost']
    )
    return response
