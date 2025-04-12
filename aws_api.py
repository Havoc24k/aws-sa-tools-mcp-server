from typing import Any
import boto3
import os
from mcp.server.fastmcp import FastMCP

# code_extensions = ('.py', '.js', '.ts', '.go', '.java', '.c', '.cpp', '.h', '.html', '.css', '.json','.yaml', '.yml', '.xml', '.sql', '.sh', '.bash', '.rb', '.php', '.swift', '.pl', '.r', '.tf')

code_extensions = ('.mjs', '.tf')

# Initialize FastMCP server
mcp = FastMCP("aws-api")


@mcp.resource("config://aws")
def get_aws_config() -> dict:
    """
    Get the AWS configuration from the user's home directory.

    Returns:
        dict: The AWS configuration.
    """
    # Get a list of all AWS profiles from the user's home directory ~/.aws/config
    config = boto3.Session().available_profiles
    return config


@mcp.resource("local://projects")
def list_local_projects() -> list:
    """
    List all folders in the ~/projects folder

    Returns:
        dict: A list containing the names of all folders in the ~/projects folder.
    """
    # Get a list of all folders in the ~/projects folder
    return os.listdir(os.path.expanduser("~/projects"))


@mcp.tool(
    name="list-local-folder",
    description="List all folders in the path"
)
def list_local_folder(path: str) -> list:
    """
    List all folders in the path

    Returns:
        dict: A list containing the names of all folders in the path folder.
    """
    # Get a list of all folders in the ~/projects folder
    return os.listdir(os.path.expanduser(path))


@mcp.tool(
    name="read-local-folder",
    description="Read all code files in the path and return the content as aa response an LLM can understand."
)
def read_local_folder(path: str) -> str:
    """
    Read all code files in the path and return the content as aa response an LLM can understand.

    Returns:
        str: A string containing the content of all code files in the path folder.
    """

    # Read all files recursively in the path
    content = ""
    for root, _, files in os.walk(os.path.expanduser(path)):
        for file in files:
            # Read the content of the file only if it is a code file
            # Ignore node_modules, .git, .terraform, and .idea folders
            if 'node_modules' in root or '.git' in root or '.terraform' in root or '.idea' in root:
                continue
            if file.endswith(code_extensions):
                with open(os.path.join(root, file), 'r') as f:
                    content += f"\n\n# {file}\n\n"
                    content += f.read() + "\n"
                    content += "\n\n"

    return content


@mcp.tool(
    name="s3-list_buckets",
    description="Get a list of all S3 buckets in the account."
)
async def s3_list_buckets(profile_name: str, region: str) -> dict:
    """
    Get a list of all S3 buckets in the account.

    Args:
        profile_name (str): The name of the AWS profile to use.
    """
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    s3 = session.client('s3', region_name=region)
    response = s3.list_buckets()
    return response


@mcp.tool(
    name="s3-list_objects",
    description="Get a list of all objects in the specified S3 bucket."
)
async def s3_list_objects(profile_name: str, region: str, bucket_name: str) -> dict:
    """
    Get a list of all objects in the specified S3 bucket.

    Args:
        profile_name (str): The name of the AWS profile to use.
        bucket_name (str): The name of the S3 bucket.
    """
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    s3 = session.client('s3', region_name=region)
    response = s3.list_objects(Bucket=bucket_name)
    return response


@mcp.tool(
    name="ce-get_cost_and_usage",
    description="Get the monthly cost of the AWS account."
)
async def ce_get_cost_and_usage(profile_name: str, region: str, group_by: str, start: str, end: str) -> dict:
    """
    Get the monthly cost of the AWS account.

    Args:
        profile_name (str): The name of the AWS profile to use.
        region (str): The AWS region to use.
        group_by (str): The dimension to group the costs by (e.g. 'SERVICE', 'AZ', 'REGION', 'INSTANCE_TYPE', etc.).
        start (str): The start date for the cost report in YYYY-MM-DD format.
        end (str): The end date for the cost report in YYYY-MM-DD format.
    """
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
    description="Get the monthly cost of the AWS account with resources."
)
async def ce_get_cost_and_usage_with_resources(profile_name: str, region: str, group_by: str, start: str, end: str) -> dict:
    """
    Get the monthly cost of the AWS account with resources.

    Args:
        profile_name (str): The name of the AWS profile to use.
        region (str): The AWS region to use.
        group_by (str): The dimension to group the costs by (e.g. 'SERVICE', 'AZ', 'REGION', 'INSTANCE_TYPE', etc.).
        start (str): The start date for the cost report in YYYY-MM-DD format.
        end (str): The end date for the cost report in YYYY-MM-DD format.
    """
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


@mcp.tool(
    name="cloudwatch-get_metric-statistics",
    description="Get the specified metric statistics for the specified metric name."
)
async def cloudwatch_get_metric_statistics(profile_name: str, region: str, metric_name: str, namespace: str, start_time: str, end_time: str, period: int) -> dict:
    """
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


@mcp.tool(
    name="ec2-describe_instances",
    description="Get a list of all EC2 instances in the account."
)
async def ec2_describe_instances(profile_name: str, region: str) -> dict:
    """
    Get a list of all EC2 instances in the account."

    Args:
        profile_name (str): The name of the AWS profile to use.
        region (str): The AWS region to use.
    """
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    ec2 = session.client('ec2', region_name=region)
    response = ec2.describe_instances()
    return response


@mcp.tool(
    name="ec2-describe_security_groups",
    description="Get a list of all security groups in the account."
)
async def ec2_describe_security_groups(profile_name: str, region: str) -> dict:
    """
    Get a list of all security groups in the account.

    Args:
        profile_name (str): The name of the AWS profile to use.
        region (str): The AWS region to use.
    """
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    ec2 = session.client('ec2', region_name=region)
    response = ec2.describe_security_groups()
    return response


@mcp.tool(
    name="ec2-describe_vpcs",
    description="Get a list of all VPCs in the account."
)
async def ec2_describe_vpcs(profile_name: str, region: str) -> dict:
    """
    Get a list of all VPCs in the account."

    Args:
        profile_name (str): The name of the AWS profile to use.
        region (str): The AWS region
    """
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    ec2 = session.client('ec2', region_name=region)
    response = ec2.describe_vpcs()
    return response


@mcp.tool(
    name="rds-describe_db_instances",
    description="Get a list of all RDS instances in the account."
)
async def rds_describe_db_instances(profile_name: str, region: str) -> dict:
    """
    Get a list of all RDS instances in the account.

    Args:
        profile_name (str): The name of the AWS profile to use.
        region (str): The AWS region to use.
    """
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    rds = session.client('rds', region_name=region)
    response = rds.describe_db_instances()
    return response


@mcp.tool(
    name="rds-describe_db_clusters",
    description="Get a list of all RDS clusters in the account."
)
async def read_terraform_remote_state(profile_name: str, region: str, bucket: str) -> dict:
    """
    Read the Terraform remote state from an S3 bucket.

    Args:
        profile_name (str): The name of the AWS profile to use.
        region (str): The AWS region to use.
        bucket (str): The name of the S3 bucket containing the Terraform remote state.
    """
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    s3 = session.client('s3', region_name=region)
    response = s3.get_object(Bucket=bucket, Key='terraform.tfstate')
    return response['Body'].read().decode('utf-8')


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
