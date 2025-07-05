import boto3
from typing import Optional, List, Dict, Any
from ...mcp import mcp


@mcp.tool(
    name="ce-get_cost_and_usage",
    description="""
    Retrieve comprehensive AWS cost and usage data with advanced filtering, grouping, and time-based analysis.

    This tool provides detailed cost analysis across AWS services, accounts, and custom dimensions.
    Essential for cost optimization, budgeting, chargeback reporting, and financial governance.
    Supports multiple granularities, cost metrics, and complex filtering for precise analysis.

    **Required Parameters:**
    - profile_name (str): AWS profile name from ~/.aws/credentials
    - region (str): AWS region (e.g., 'us-east-1') - Cost Explorer is global but requires region
    - start (str): Start date in YYYY-MM-DD format (e.g., '2024-01-01')
    - end (str): End date in YYYY-MM-DD format (e.g., '2024-01-31')
      * Maximum 12 months range for daily data
      * Maximum 12 months range for monthly data
      * Maximum 1 week range for hourly data

    **Optional Parameters:**
    - granularity (str): Time granularity for cost breakdown. Default: 'MONTHLY'
      * 'DAILY': Day-by-day cost breakdown (max 12 months)
      * 'MONTHLY': Month-by-month cost breakdown (max 12 months)
      * 'HOURLY': Hour-by-hour cost breakdown (max 1 week)
    
    - group_by (List[Dict[str, str]]): Grouping dimensions for cost analysis
      **Service Grouping:**
      [{'Type': 'DIMENSION', 'Key': 'SERVICE'}] - Group by AWS service
      
      **Account Grouping:**
      [{'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'}] - Group by AWS account
      
      **Geographic Grouping:**
      [{'Type': 'DIMENSION', 'Key': 'REGION'}] - Group by AWS region
      [{'Type': 'DIMENSION', 'Key': 'AVAILABILITY_ZONE'}] - Group by AZ
      
      **Resource Grouping:**
      [{'Type': 'DIMENSION', 'Key': 'INSTANCE_TYPE'}] - Group by EC2 instance type
      [{'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}] - Group by usage type
      [{'Type': 'DIMENSION', 'Key': 'OPERATION'}] - Group by operation
      
      **Tag-based Grouping:**
      [{'Type': 'TAG', 'Key': 'Environment'}] - Group by Environment tag
      [{'Type': 'TAG', 'Key': 'Project'}] - Group by Project tag
      [{'Type': 'TAG', 'Key': 'Owner'}] - Group by Owner tag
      
      **Multiple Grouping:**
      [{'Type': 'DIMENSION', 'Key': 'SERVICE'}, {'Type': 'TAG', 'Key': 'Environment'}]
    
    - metrics (List[str]): Cost metrics to retrieve. Default: ['BlendedCost']
      * 'BlendedCost': Cost after applying Reserved Instance and Savings Plans discounts
      * 'UnblendedCost': On-demand cost without discounts
      * 'NetBlendedCost': BlendedCost minus credits and refunds
      * 'NetUnblendedCost': UnblendedCost minus credits and refunds
      * 'UsageQuantity': Usage amount (hours, GB, requests, etc.)
      * 'NormalizedUsageAmount': Usage normalized to equivalent units
    
    - filter_expression (Dict[str, Any]): Advanced filtering for targeted analysis
      **Service Filters:**
      {'Dimensions': {'Key': 'SERVICE', 'Values': ['Amazon Elastic Compute Cloud - Compute']}}
      
      **Account Filters:**
      {'Dimensions': {'Key': 'LINKED_ACCOUNT', 'Values': ['123456789012']}}
      
      **Region Filters:**
      {'Dimensions': {'Key': 'REGION', 'Values': ['us-east-1', 'us-west-2']}}
      
      **Tag Filters:**
      {'Tags': {'Key': 'Environment', 'Values': ['production', 'staging']}}
      
      **Complex Filters (AND/OR/NOT):**
      {'And': [{'Dimensions': {'Key': 'SERVICE', 'Values': ['EC2']}}, {'Tags': {'Key': 'Environment', 'Values': ['production']}}]}
    
    - next_page_token (str): Pagination token from previous response
      * Use NextPageToken from previous call for large datasets

    **Common Use Cases:**
    1. **Monthly service breakdown:** granularity='MONTHLY', group_by=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    2. **Daily cost trends:** granularity='DAILY', metrics=['BlendedCost']
    3. **Environment cost analysis:** group_by=[{'Type': 'TAG', 'Key': 'Environment'}]
    4. **EC2 cost optimization:** filter_expression={'Dimensions': {'Key': 'SERVICE', 'Values': ['Amazon Elastic Compute Cloud - Compute']}}
    5. **Multi-account analysis:** group_by=[{'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'}]
    6. **Regional cost comparison:** group_by=[{'Type': 'DIMENSION', 'Key': 'REGION'}]

    **Response includes:** Time periods, cost amounts by specified metrics, grouping dimensions,
    and metadata for comprehensive cost analysis and reporting.

    **Best Practices:**
    - Use monthly granularity for trend analysis
    - Apply service filters to focus on specific cost areas
    - Combine dimension and tag grouping for detailed insights
    - Use pagination for large datasets
    - Consider NetBlendedCost for accurate cost reporting
    """
)
async def ce_get_cost_and_usage(
    profile_name: str, 
    region: str, 
    start: str, 
    end: str,
    granularity: Optional[str] = 'MONTHLY',
    group_by: Optional[List[Dict[str, str]]] = None,
    metrics: Optional[List[str]] = None,
    filter_expression: Optional[Dict[str, Any]] = None,
    next_page_token: Optional[str] = None
) -> dict:
    session = boto3.Session(profile_name=profile_name)
    ce = session.client('ce', region_name=region)
    
    params = {
        'TimePeriod': {'Start': start, 'End': end},
        'Granularity': granularity,
        'Metrics': metrics or ['BlendedCost']
    }
    
    if group_by:
        params['GroupBy'] = group_by
    if filter_expression:
        params['Filter'] = filter_expression
    if next_page_token:
        params['NextPageToken'] = next_page_token
    
    response = ce.get_cost_and_usage(**params)
    return response


@mcp.tool(
    name="ce-get_cost_and_usage_with_resources",
    description="""
    Retrieve detailed AWS cost and usage data with individual resource-level granularity and identification.

    This tool provides the most granular cost analysis available, showing costs for individual AWS resources
    such as specific EC2 instances, RDS databases, and S3 buckets. Essential for detailed cost allocation,
    rightsizing analysis, and identifying cost optimization opportunities at the resource level.

    **Required Parameters:**
    - profile_name (str): AWS profile name from ~/.aws/credentials
    - region (str): AWS region (e.g., 'us-east-1') - Cost Explorer is global but requires region
    - start (str): Start date in YYYY-MM-DD format (e.g., '2024-01-01')
    - end (str): End date in YYYY-MM-DD format (e.g., '2024-01-31')
      * **Note:** Maximum 14 days range for resource-level data
      * Hourly granularity not supported for resource-level analysis

    **Optional Parameters:**
    - granularity (str): Time granularity for cost breakdown. Default: 'MONTHLY'
      * 'DAILY': Day-by-day resource cost breakdown (max 14 days)
      * 'MONTHLY': Month-by-month resource cost breakdown (max 14 days)
      * **Note:** HOURLY not supported for resource-level data
    
    - group_by (List[Dict[str, str]]): Grouping dimensions for resource analysis
      **Resource Grouping:**
      [{'Type': 'DIMENSION', 'Key': 'RESOURCE_ID'}] - Group by individual resources
      
      **Service + Resource:**
      [{'Type': 'DIMENSION', 'Key': 'SERVICE'}, {'Type': 'DIMENSION', 'Key': 'RESOURCE_ID'}]
      
      **Tag-based Resource Analysis:**
      [{'Type': 'TAG', 'Key': 'Name'}, {'Type': 'DIMENSION', 'Key': 'RESOURCE_ID'}]
      [{'Type': 'TAG', 'Key': 'Environment'}, {'Type': 'DIMENSION', 'Key': 'RESOURCE_ID'}]
    
    - metrics (List[str]): Cost metrics to retrieve. Default: ['BlendedCost']
      * 'BlendedCost': Cost after applying Reserved Instance and Savings Plans discounts
      * 'UnblendedCost': On-demand cost without discounts
      * 'NetBlendedCost': BlendedCost minus credits and refunds
      * 'NetUnblendedCost': UnblendedCost minus credits and refunds
      * 'UsageQuantity': Resource usage amount (hours, GB, requests, etc.)
      * 'NormalizedUsageAmount': Usage normalized to equivalent units
    
    - filter_expression (Dict[str, Any]): Advanced filtering for targeted resource analysis
      **Service Filters:**
      {'Dimensions': {'Key': 'SERVICE', 'Values': ['Amazon Elastic Compute Cloud - Compute']}}
      
      **Resource Type Filters:**
      {'Dimensions': {'Key': 'INSTANCE_TYPE', 'Values': ['t3.micro', 'm5.large']}}
      
      **Tag-based Resource Filters:**
      {'Tags': {'Key': 'Environment', 'Values': ['production']}}
      {'Tags': {'Key': 'Owner', 'Values': ['team-a', 'team-b']}}
      
      **Complex Resource Filters:**
      {'And': [{'Dimensions': {'Key': 'SERVICE', 'Values': ['EC2']}}, {'Tags': {'Key': 'Environment', 'Values': ['production']}}]}
    
    - next_page_token (str): Pagination token from previous response
      * Essential for resource-level data due to large result sets

    **Common Use Cases:**
    1. **EC2 instance cost analysis:** 
       filter_expression={'Dimensions': {'Key': 'SERVICE', 'Values': ['Amazon Elastic Compute Cloud - Compute']}}
       group_by=[{'Type': 'DIMENSION', 'Key': 'RESOURCE_ID'}]
    
    2. **RDS database cost breakdown:**
       filter_expression={'Dimensions': {'Key': 'SERVICE', 'Values': ['Amazon Relational Database Service']}}
       group_by=[{'Type': 'DIMENSION', 'Key': 'RESOURCE_ID'}]
    
    3. **S3 bucket cost analysis:**
       filter_expression={'Dimensions': {'Key': 'SERVICE', 'Values': ['Amazon Simple Storage Service']}}
       group_by=[{'Type': 'DIMENSION', 'Key': 'RESOURCE_ID'}]
    
    4. **Team-based resource costs:**
       filter_expression={'Tags': {'Key': 'Team', 'Values': ['backend', 'frontend']}}
       group_by=[{'Type': 'TAG', 'Key': 'Team'}, {'Type': 'DIMENSION', 'Key': 'RESOURCE_ID'}]
    
    5. **Environment resource breakdown:**
       filter_expression={'Tags': {'Key': 'Environment', 'Values': ['production']}}
       group_by=[{'Type': 'DIMENSION', 'Key': 'RESOURCE_ID'}]

    **Response includes:** Time periods, individual resource identifiers, cost amounts,
    resource metadata, and grouping dimensions for granular cost analysis.

    **Important Limitations:**
    - Maximum 14-day date range (AWS limitation for resource-level data)
    - Large result sets require pagination
    - Not all services provide resource-level cost data
    - Higher API costs compared to standard cost analysis

    **Best Practices:**
    - Use specific service filters to reduce data volume
    - Implement pagination for comprehensive analysis
    - Focus on high-cost services for optimization
    - Combine with tagging strategies for better insights
    - Use for detailed cost allocation and chargeback reporting
    """
)
async def ce_get_cost_and_usage_with_resources(
    profile_name: str, 
    region: str, 
    start: str, 
    end: str,
    granularity: Optional[str] = 'MONTHLY',
    group_by: Optional[List[Dict[str, str]]] = None,
    metrics: Optional[List[str]] = None,
    filter_expression: Optional[Dict[str, Any]] = None,
    next_page_token: Optional[str] = None
) -> dict:
    session = boto3.Session(profile_name=profile_name)
    ce = session.client('ce', region_name=region)
    
    params = {
        'TimePeriod': {'Start': start, 'End': end},
        'Granularity': granularity,
        'Metrics': metrics or ['BlendedCost']
    }
    
    if group_by:
        params['GroupBy'] = group_by
    if filter_expression:
        params['Filter'] = filter_expression
    if next_page_token:
        params['NextPageToken'] = next_page_token
    
    response = ce.get_cost_and_usage_with_resources(**params)
    return response
