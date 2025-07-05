from typing import Any

import boto3

from ...mcp import mcp


@mcp.tool(
    name="rds-describe_db_instances",
    description="""
    Retrieve comprehensive RDS database instance information with advanced filtering and pagination.

    This tool provides detailed information about RDS database instances including configuration,
    status, performance settings, and security details. Essential for database monitoring,
    compliance auditing, and operational management.

    **Required Parameters:**
    - profile_name (str): AWS profile name from ~/.aws/credentials
    - region (str): AWS region (e.g., 'us-east-1', 'eu-west-1')

    **Optional Parameters:**
    - db_instance_identifier (str): Specific database instance identifier
      Example: 'production-mysql-db', 'staging-postgres-01'

    - filters (Dict[str, Any]): Advanced filtering options
      **Engine Filters:**
      - 'engine': Database engine types
        * MySQL: ['mysql']
        * PostgreSQL: ['postgres']
        * Oracle: ['oracle-ee', 'oracle-se2', 'oracle-se1', 'oracle-se']
        * SQL Server: ['sqlserver-ex', 'sqlserver-web', 'sqlserver-se', 'sqlserver-ee']
        * MariaDB: ['mariadb']
        * Aurora: ['aurora-mysql', 'aurora-postgresql']

      **Version Filters:**
      - 'engine-version': ['8.0.35', '13.7', '19.0.0.0.ru-2023-01.rur-2023-01.r1']

      **Instance Class Filters:**
      - 'db-instance-class': ['db.t3.micro', 'db.r5.large', 'db.m5.xlarge']

      **Status Filters:**
      - 'db-instance-status': ['available', 'creating', 'deleting', 'modifying', 'rebooting', 'stopped']

      **Network Filters:**
      - 'vpc-id': ['vpc-12345678'] - Filter by VPC
      - 'subnet-group-name': ['default', 'custom-subnet-group']

      **Availability Filters:**
      - 'availability-zone': ['us-east-1a', 'us-east-1b']
      - 'multi-az': ['true', 'false'] - Multi-AZ deployment filter

      **Security Filters:**
      - 'db-security-group': ['sg-12345678'] - VPC security groups
      - 'db-parameter-group': ['default.mysql8.0', 'custom-params']

      **Backup and Maintenance:**
      - 'backup-retention-period': ['7', '14', '30'] - Backup retention days
      - 'maintenance-window': ['sun:05:00-sun:06:00'] - Maintenance window

      **Performance Insights:**
      - 'performance-insights-enabled': ['true', 'false']
      - 'monitoring-interval': ['0', '60', '300'] - Enhanced monitoring interval

    - max_records (int): Maximum results per request (20-100)
      * Default: 100
      * Use smaller values for memory efficiency
      * Combine with pagination for large fleets

    - marker (str): Pagination marker from previous response
      * Use 'Marker' value from previous call
      * Enables seamless pagination through large DB fleets

    **Common Use Cases:**
    1. **Production DB audit:** filters={'engine': ['mysql'], 'db-instance-status': ['available']}
    2. **Multi-AZ check:** filters={'multi-az': ['true']}
    3. **Security audit:** filters={'vpc-id': ['vpc-12345678']}
    4. **Performance monitoring:** filters={'performance-insights-enabled': ['true']}
    5. **Backup compliance:** filters={'backup-retention-period': ['7', '14', '30']}
    6. **Engine version check:** filters={'engine': ['mysql'], 'engine-version': ['8.0.35']}

    **Response includes:** DB instance identifier, status, engine details, instance class,
    availability zone, VPC security groups, parameter groups, backup settings, performance
    insights status, monitoring configuration, endpoint information, and more.

    **Use Cases:**
    - Database inventory and compliance reporting
    - Performance monitoring and optimization
    - Security auditing and configuration review
    - Backup and disaster recovery planning
    - Cost optimization and rightsizing analysis

    Essential for comprehensive RDS fleet management and operational visibility.
    """,
)
async def rds_describe_db_instances(
    profile_name: str,
    region: str,
    db_instance_identifier: str | None = None,
    filters: dict[str, list[Any]] | None = None,
    max_records: int | None = None,
    marker: str | None = None,
) -> Any:
    session = boto3.Session(profile_name=profile_name)
    rds = session.client("rds", region_name=region)

    params: dict[str, Any] = {}
    if db_instance_identifier:
        params["DBInstanceIdentifier"] = db_instance_identifier
    if filters:
        params["Filters"] = [
            {"Name": k, "Values": v if isinstance(v, list) else [v]}
            for k, v in filters.items()
        ]
    if max_records:
        params["MaxRecords"] = max_records
    if marker:
        params["Marker"] = marker

    response = rds.describe_db_instances(**params)
    return response
