from typing import Any

import boto3

from ...mcp import mcp


@mcp.tool(
    name="cloudwatch-get_metric_statistics",
    description="""
    Retrieve CloudWatch metric statistics with full configurability for monitoring AWS resources.

    This tool fetches time-series data points for CloudWatch metrics, supporting custom statistics,
    dimensions, and time ranges. Essential for monitoring EC2 instances, RDS databases, Lambda functions,
    and other AWS services.

    **Required Parameters:**
    - profile_name (str): AWS profile name from ~/.aws/credentials
    - region (str): AWS region (e.g., 'us-east-1', 'eu-west-1')
    - metric_name (str): CloudWatch metric name (e.g., 'CPUUtilization', 'NetworkIn', 'DatabaseConnections')
    - namespace (str): AWS service namespace (e.g., 'AWS/EC2', 'AWS/RDS', 'AWS/Lambda')
    - start_time (str): Start time in ISO 8601 format (e.g., '2024-01-01T00:00:00Z')
    - end_time (str): End time in ISO 8601 format (e.g., '2024-01-02T00:00:00Z')
    - period (int): Data point interval in seconds (60, 300, 3600, etc. - must align with metric resolution)

    **Optional Parameters:**
    - statistics (List[str]): Standard statistics to calculate. Default: ['Average']
      Options: 'Average', 'Sum', 'SampleCount', 'Maximum', 'Minimum'
      Example: ['Average', 'Maximum'] for CPU utilization trends

    - extended_statistics (List[str]): Percentile statistics for detailed analysis
      Format: 'p{percentile}' (e.g., 'p99', 'p95', 'p90', 'p50')
      Example: ['p99', 'p95'] for latency analysis

    - dimensions (List[Dict[str, str]]): Filter metrics by specific resource attributes
      Common dimension examples:
      * EC2: [{'Name': 'InstanceId', 'Value': 'i-1234567890abcdef0'}]
      * RDS: [{'Name': 'DBInstanceIdentifier', 'Value': 'mydb-instance'}]
      * Lambda: [{'Name': 'FunctionName', 'Value': 'my-function'}]
      * ELB: [{'Name': 'LoadBalancerName', 'Value': 'my-load-balancer'}]

    - unit (str): Expected unit of measurement for validation
      Common units: 'Seconds', 'Percent', 'Count', 'Bytes', 'Bits/Second'

    **Common Use Cases:**
    1. Monitor EC2 CPU: namespace='AWS/EC2', metric_name='CPUUtilization', statistics=['Average', 'Maximum']
    2. Track RDS connections: namespace='AWS/RDS', metric_name='DatabaseConnections', statistics=['Average']
    3. Lambda duration analysis: namespace='AWS/Lambda', metric_name='Duration', extended_statistics=['p99', 'p95']
    4. ELB response times: namespace='AWS/ELB', metric_name='Latency', extended_statistics=['p95', 'p99']

    **Time Range Guidelines:**
    - For high-resolution metrics: Use 60-second periods, max 3 hours of data
    - For standard metrics: Use 300-second periods, up to 15 days of data
    - For long-term analysis: Use 3600-second periods, up to 455 days of data

    Returns detailed metric data points with timestamps, values, and units for analysis and alerting.
    """,
)
async def cloudwatch_get_metric_statistics(
    profile_name: str,
    region: str,
    metric_name: str,
    namespace: str,
    start_time: str,
    end_time: str,
    period: int,
    statistics: list[str] | None = None,
    extended_statistics: list[str] | None = None,
    dimensions: list[dict[str, str]] | None = None,
    unit: str | None = None,
) -> dict:
    session = boto3.Session(profile_name=profile_name)
    cloudwatch = session.client("cloudwatch", region_name=region)

    params = {
        "Namespace": namespace,
        "MetricName": metric_name,
        "StartTime": start_time,
        "EndTime": end_time,
        "Period": period,
    }

    if statistics:
        params["Statistics"] = statistics
    elif not extended_statistics:
        params["Statistics"] = ["Average"]

    if extended_statistics:
        params["ExtendedStatistics"] = extended_statistics

    if dimensions:
        params["Dimensions"] = dimensions

    if unit:
        params["Unit"] = unit

    response = cloudwatch.get_metric_statistics(**params)
    return response
