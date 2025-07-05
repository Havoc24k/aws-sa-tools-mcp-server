import boto3
from typing import Optional, List, Dict, Any
from ...mcp import mcp


@mcp.tool(
    name="ec2-describe_instances",
    description="""
    Retrieve detailed information about EC2 instances with advanced filtering and pagination.

    This tool provides comprehensive instance data including state, type, networking, tags, and configuration.
    Essential for inventory management, monitoring, and troubleshooting EC2 infrastructure.

    **Required Parameters:**
    - profile_name (str): AWS profile name from ~/.aws/credentials
    - region (str): AWS region (e.g., 'us-east-1', 'eu-west-1')

    **Optional Parameters:**
    - instance_ids (List[str]): Specific instance IDs to retrieve
      Example: ['i-1234567890abcdef0', 'i-0987654321fedcba0']
    
    - filters (Dict[str, Any]): Advanced filtering options
      **Instance State Filters:**
      - 'instance-state-name': ['pending', 'running', 'shutting-down', 'terminated', 'stopping', 'stopped']
      
      **Instance Type Filters:**
      - 'instance-type': ['t2.micro', 't3.small', 'm5.large', 'c5.xlarge']
      
      **Network Filters:**
      - 'vpc-id': ['vpc-12345678'] - Filter by VPC
      - 'subnet-id': ['subnet-12345678'] - Filter by subnet
      - 'private-ip-address': ['10.0.1.100'] - Filter by private IP
      - 'public-ip-address': ['54.123.45.67'] - Filter by public IP
      
      **Tag Filters:**
      - 'tag:Name': ['web-server', 'database'] - Filter by Name tag
      - 'tag:Environment': ['production', 'staging'] - Filter by Environment tag
      - 'tag-key': ['Owner'] - Filter by tag key existence
      
      **Security and Compliance:**
      - 'security-group-id': ['sg-12345678'] - Filter by security group
      - 'key-name': ['my-key-pair'] - Filter by key pair
      - 'monitoring-state': ['enabled', 'disabled'] - Filter by detailed monitoring
      
      **Architecture Filters:**
      - 'architecture': ['i386', 'x86_64', 'arm64'] - Filter by architecture
      - 'root-device-type': ['ebs', 'instance-store'] - Filter by root device type
      - 'virtualization-type': ['hvm', 'paravirtual'] - Filter by virtualization
    
    - max_results (int): Limit results (1-1000). Default: no limit
    - next_token (str): Pagination token from previous request

    **Common Use Cases:**
    1. List all running instances: filters={'instance-state-name': ['running']}
    2. Find instances by tag: filters={'tag:Environment': ['production']}
    3. Get instances in specific VPC: filters={'vpc-id': ['vpc-12345678']}
    4. Find instances by type: filters={'instance-type': ['t3.micro', 't3.small']}
    5. Security audit: filters={'security-group-id': ['sg-12345678']}

    **Response includes:** Instance ID, state, type, AMI ID, key name, launch time, 
    networking details, security groups, tags, monitoring state, and more.
    
    Use pagination with max_results and next_token for large environments.
    """
)
async def ec2_describe_instances(
    profile_name: str, 
    region: str,
    instance_ids: Optional[List[str]] = None,
    filters: Optional[Dict[str, Any]] = None,
    max_results: Optional[int] = None,
    next_token: Optional[str] = None
) -> dict:
    session = boto3.Session(profile_name=profile_name)
    ec2 = session.client('ec2', region_name=region)
    
    params = {}
    if instance_ids:
        params['InstanceIds'] = instance_ids
    if filters:
        params['Filters'] = [{'Name': k, 'Values': v if isinstance(v, list) else [v]} for k, v in filters.items()]
    if max_results:
        params['MaxResults'] = max_results
    if next_token:
        params['NextToken'] = next_token
    
    response = ec2.describe_instances(**params)
    return response


@mcp.tool(
    name="ec2-describe_security_groups",
    description="""
    Retrieve detailed security group information with comprehensive filtering for network security analysis.

    This tool provides complete security group data including ingress/egress rules, associated resources,
    and tags. Critical for security auditing, compliance checking, and network troubleshooting.

    **Required Parameters:**
    - profile_name (str): AWS profile name from ~/.aws/credentials
    - region (str): AWS region (e.g., 'us-east-1', 'eu-west-1')

    **Optional Parameters:**
    - group_ids (List[str]): Specific security group IDs to retrieve
      Example: ['sg-12345678', 'sg-87654321']
    
    - group_names (List[str]): Security group names (VPC security groups use IDs, not names)
      Example: ['web-server-sg', 'database-sg']
    
    - filters (Dict[str, Any]): Advanced filtering options
      **Basic Filters:**
      - 'group-name': ['web-server-sg', 'database-sg'] - Filter by name
      - 'group-id': ['sg-12345678'] - Filter by ID
      - 'description': ['Web server security group'] - Filter by description
      
      **Network Filters:**
      - 'vpc-id': ['vpc-12345678'] - Filter by VPC (most common)
      - 'owner-id': ['123456789012'] - Filter by AWS account ID
      
      **Rule-based Filters:**
      - 'ip-protocol': ['tcp', 'udp', 'icmp'] - Filter by protocol
      - 'from-port': [22, 80, 443] - Filter by port range start
      - 'to-port': [22, 80, 443] - Filter by port range end
      - 'cidr': ['10.0.0.0/16', '0.0.0.0/0'] - Filter by CIDR block
      
      **Tag Filters:**
      - 'tag:Name': ['web-tier', 'db-tier'] - Filter by Name tag
      - 'tag:Environment': ['production', 'staging'] - Filter by Environment tag
      - 'tag-key': ['Owner'] - Filter by tag key existence
    
    - max_results (int): Limit results (5-1000). Default: no limit
    - next_token (str): Pagination token from previous request

    **Common Use Cases:**
    1. Audit VPC security groups: filters={'vpc-id': ['vpc-12345678']}
    2. Find groups allowing SSH: filters={'from-port': [22], 'to-port': [22]}
    3. Security compliance check: filters={'cidr': ['0.0.0.0/0']} (find public access)
    4. Find groups by tag: filters={'tag:Environment': ['production']}
    5. Owner-based filtering: filters={'owner-id': ['123456789012']}

    **Response includes:** Group ID, name, description, VPC ID, owner ID, ingress/egress rules 
    (with ports, protocols, source/destination), tags, and associated resources.
    
    Essential for security auditing and network access control management.
    """
)
async def ec2_describe_security_groups(
    profile_name: str, 
    region: str,
    group_ids: Optional[List[str]] = None,
    group_names: Optional[List[str]] = None,
    filters: Optional[Dict[str, Any]] = None,
    max_results: Optional[int] = None,
    next_token: Optional[str] = None
) -> dict:
    session = boto3.Session(profile_name=profile_name)
    ec2 = session.client('ec2', region_name=region)
    
    params = {}
    if group_ids:
        params['GroupIds'] = group_ids
    if group_names:
        params['GroupNames'] = group_names
    if filters:
        params['Filters'] = [{'Name': k, 'Values': v if isinstance(v, list) else [v]} for k, v in filters.items()]
    if max_results:
        params['MaxResults'] = max_results
    if next_token:
        params['NextToken'] = next_token
    
    response = ec2.describe_security_groups(**params)
    return response


@mcp.tool(
    name="ec2-describe_vpcs",
    description="""
    Retrieve comprehensive VPC information with advanced filtering for network infrastructure analysis.

    This tool provides complete VPC data including CIDR blocks, DNS settings, tenancy, and associated 
    resources. Essential for network planning, security auditing, and infrastructure management.

    **Required Parameters:**
    - profile_name (str): AWS profile name from ~/.aws/credentials
    - region (str): AWS region (e.g., 'us-east-1', 'eu-west-1')

    **Optional Parameters:**
    - vpc_ids (List[str]): Specific VPC IDs to retrieve
      Example: ['vpc-12345678', 'vpc-87654321']
    
    - filters (Dict[str, Any]): Advanced filtering options
      **State Filters:**
      - 'state': ['pending', 'available'] - Filter by VPC state
      
      **Network Configuration:**
      - 'cidr': ['10.0.0.0/16', '172.16.0.0/12'] - Filter by primary CIDR block
      - 'cidr-block-association.cidr-block': ['10.1.0.0/16'] - Filter by any CIDR block
      - 'cidr-block-association.state': ['associated', 'associating', 'disassociated']
      
      **DNS and Networking:**
      - 'dhcp-options-id': ['dopt-12345678'] - Filter by DHCP options set
      - 'dns-resolution': ['true', 'false'] - Filter by DNS resolution support
      - 'dns-hostnames': ['true', 'false'] - Filter by DNS hostnames support
      
      **Default VPC:**
      - 'is-default': ['true', 'false'] - Filter default vs custom VPCs
      
      **Tenancy:**
      - 'instance-tenancy': ['default', 'dedicated', 'host'] - Filter by instance tenancy
      
      **Ownership:**
      - 'owner-id': ['123456789012'] - Filter by AWS account ID
      
      **Tag Filters:**
      - 'tag:Name': ['production-vpc', 'staging-vpc'] - Filter by Name tag
      - 'tag:Environment': ['production', 'staging'] - Filter by Environment tag
      - 'tag-key': ['Owner'] - Filter by tag key existence
    
    - max_results (int): Limit results (5-1000). Default: no limit
    - next_token (str): Pagination token from previous request

    **Common Use Cases:**
    1. Find default VPC: filters={'is-default': ['true']}
    2. List production VPCs: filters={'tag:Environment': ['production']}
    3. Find VPCs with specific CIDR: filters={'cidr': ['10.0.0.0/16']}
    4. Audit DNS settings: filters={'dns-resolution': ['true']}
    5. Check tenancy: filters={'instance-tenancy': ['dedicated']}

    **Response includes:** VPC ID, state, CIDR blocks, DNS resolution settings, DHCP options,
    instance tenancy, default VPC flag, owner ID, tags, and associated CIDR block associations.
    
    Critical for network architecture planning and security compliance auditing.
    """
)
async def ec2_describe_vpcs(
    profile_name: str, 
    region: str,
    vpc_ids: Optional[List[str]] = None,
    filters: Optional[Dict[str, Any]] = None,
    max_results: Optional[int] = None,
    next_token: Optional[str] = None
) -> dict:
    session = boto3.Session(profile_name=profile_name)
    ec2 = session.client('ec2', region_name=region)
    
    params = {}
    if vpc_ids:
        params['VpcIds'] = vpc_ids
    if filters:
        params['Filters'] = [{'Name': k, 'Values': v if isinstance(v, list) else [v]} for k, v in filters.items()]
    if max_results:
        params['MaxResults'] = max_results
    if next_token:
        params['NextToken'] = next_token
    
    response = ec2.describe_vpcs(**params)
    return response
