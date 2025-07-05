from typing import Any, Optional

import boto3

from ...mcp import mcp


@mcp.tool(
    name="s3-list_buckets",
    description="""
    Retrieve all S3 buckets in the AWS account with creation timestamps.

    This tool lists all S3 buckets across all regions for the specified AWS account.
    S3 buckets are globally unique and region-independent for listing operations.
    Essential for storage inventory, cost analysis, and compliance auditing.

    **Required Parameters:**
    - profile_name (str): AWS profile name from ~/.aws/credentials

    **Optional Parameters:**
    - region (str): AWS region (not used for bucket listing but required for consistency)

    **Response includes:** Bucket name, creation date, and owner information.

    **Common Use Cases:**
    1. Storage inventory and auditing
    2. Cost analysis preparation
    3. Compliance and governance reporting
    4. Cross-region bucket discovery
    5. Backup and disaster recovery planning

    **Note:** This operation lists all buckets regardless of region. Use s3-list_objects_v2
    to explore bucket contents and get region-specific bucket information.
    """,
)
async def s3_list_buckets(profile_name: str, region: str) -> Any:
    # Get the AWS credentials
    session = boto3.Session(profile_name=profile_name)
    s3 = session.client("s3", region_name=region)
    response = s3.list_buckets()
    return response


@mcp.tool(
    name="s3-list_objects_v2",
    description="""
    List S3 bucket objects with advanced filtering, pagination, and hierarchical browsing capabilities.

    This tool uses the latest S3 API (ListObjectsV2) for optimal performance and features.
    Supports prefix filtering, folder-like navigation, and efficient pagination for large buckets.
    Essential for content management, backup operations, and storage analysis.

    **Required Parameters:**
    - profile_name (str): AWS profile name from ~/.aws/credentials
    - region (str): AWS region where the bucket resides (e.g., 'us-east-1', 'eu-west-1')
    - bucket_name (str): S3 bucket name (must exist and be accessible)

    **Optional Parameters:**
    - prefix (str): Filter objects by key prefix for targeted listing
      Examples:
      * 'logs/' - List all objects in logs folder
      * 'images/2024/' - List objects in images/2024 path
      * 'backup-' - List objects starting with 'backup-'

    - delimiter (str): Character for hierarchical grouping (typically '/')
      * Use '/' for folder-like navigation
      * Returns CommonPrefixes for "folders"
      * Enables efficient directory-style browsing

    - max_keys (int): Limit results per request (1-1000)
      * Default: 1000 (AWS maximum)
      * Use smaller values for memory efficiency
      * Combine with pagination for large datasets

    - continuation_token (str): Token from previous response for pagination
      * Use NextContinuationToken from previous call
      * Enables seamless pagination through large buckets

    - start_after (str): Start listing after this key name
      * Useful for resuming interrupted operations
      * Lexicographically ordered starting point

    - fetch_owner (bool): Include owner information in response
      * Default: false (for performance)
      * Set to true for detailed ownership data
      * Useful for security auditing

    **Common Use Cases:**
    1. **Folder browsing:** delimiter='/', prefix='photos/'
    2. **File search:** prefix='log-2024-', max_keys=100
    3. **Large bucket pagination:** max_keys=1000, continuation_token=<token>
    4. **Date-based filtering:** prefix='backups/2024/01/'
    5. **Ownership audit:** fetch_owner=true
    6. **Resume operations:** start_after='last-processed-key'

    **Response includes:** Object keys, sizes, last modified dates, ETags, storage classes,
    and optionally owner information. Also includes CommonPrefixes for folder-like structures.

    **Performance Tips:**
    - Use prefix filtering to reduce response size
    - Implement pagination for buckets with >1000 objects
    - Use delimiter for efficient folder navigation
    - Consider fetch_owner=false for better performance
    """,
)
async def s3_list_objects_v2(
    profile_name: str,
    region: str,
    bucket_name: str,
    prefix: str | None = None,
    delimiter: str | None = None,
    max_keys: int | None = None,
    continuation_token: str | None = None,
    start_after: str | None = None,
    fetch_owner: bool | None = None,
) -> Any:
    session = boto3.Session(profile_name=profile_name)
    s3 = session.client("s3", region_name=region)

    params = {"Bucket": bucket_name}
    if prefix:
        params["Prefix"] = prefix
    if delimiter:
        params["Delimiter"] = delimiter
    if max_keys:
        params["MaxKeys"] = str(max_keys)
    if continuation_token:
        params["ContinuationToken"] = continuation_token
    if start_after:
        params["StartAfter"] = start_after
    if fetch_owner is not None:
        params["FetchOwner"] = str(fetch_owner).lower()

    response = s3.list_objects_v2(**params)
    return response
