from typing import Any

from ...core.utils import build_params, create_aws_client
from ...mcp import mcp


@mcp.tool(
    name="s3-list_buckets",
    description="List all S3 buckets in the AWS account",
)
async def s3_list_buckets(profile_name: str, region: str) -> Any:
    s3 = create_aws_client(profile_name, region, "s3")
    return s3.list_buckets()


@mcp.tool(
    name="s3-list_objects_v2",
    description="List objects in an S3 bucket with filtering and pagination",
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
