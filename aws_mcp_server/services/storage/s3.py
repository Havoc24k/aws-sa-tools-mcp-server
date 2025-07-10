from typing import Any

from ...mcp import mcp


# Modern implementation - reduced from ~30 lines to 8 lines
@mcp.tool(
    name="s3-list_buckets",
    description="""List all S3 buckets in the AWS account.

    Retrieves bucket names, creation dates, and owner information.
    Essential for storage inventory and cost analysis.""",
)
async def s3_list_buckets(profile_name: str, region: str) -> Any:
    from ...core.utils import create_aws_client
    s3 = create_aws_client(profile_name, region, "s3")
    return s3.list_buckets()


# Modern implementation - reduced from ~80 lines to 15 lines
@mcp.tool(
    name="s3-list_objects_v2",
    description="""List objects in an S3 bucket with filtering and pagination.

    Uses S3 ListObjectsV2 API for optimal performance. Supports prefix filtering,
    folder-like navigation, and efficient pagination for large buckets.

    Parameters:
    - bucket_name: S3 bucket name
    - prefix: Filter objects by key prefix (optional)
    - delimiter: Character for hierarchical grouping (optional)
    - max_keys: Maximum results per request (1-1000, optional)
    - continuation_token: Token for pagination (optional)
    - start_after: Start listing after this key (optional)
    - fetch_owner: Include owner information (optional)""",
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
    from ...core.utils import build_params, create_aws_client

    s3 = create_aws_client(profile_name, region, "s3")
    params = build_params(
        Bucket=bucket_name,
        Prefix=prefix,
        Delimiter=delimiter,
        MaxKeys=max_keys,
        ContinuationToken=continuation_token,
        StartAfter=start_after,
        FetchOwner=str(fetch_owner).lower() if fetch_owner is not None else None,
    )
    return s3.list_objects_v2(**params)
