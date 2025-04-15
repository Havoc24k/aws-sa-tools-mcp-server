import boto3
from aws_mcp.mcp import mcp


@mcp.tool(
    name="cloudwatch-get_metric-statistics",
    description="""
    Get the specified metric statistics for the specified metric name.

    Args:
        profile_name (str): The name of the AWS profile to use.
        region (str): The AWS region to use.
        metric_name (str): The name of the metric to get statistics for.
        namespace (str): The namespace of the metric.
        start_time (str): The start time for the statistics in ISO 8601 format.
        end_time (str): The end time for the statistics in ISO 8601 format.
        period (int): The granularity, in seconds, of the returned data points.
    """
)
async def cloudwatch_get_metric_statistics(profile_name: str, region: str, metric_name: str, namespace: str, start_time: str, end_time: str, period: int) -> dict:
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    cloudwatch = session.client('cloudwatch', region_name=region)
    response = cloudwatch.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        StartTime=start_time,
        EndTime=end_time,
        Period=period,
        Statistics=['Average', 'Sum']
    )
    return response
