"""Utility functions for AWS MCP server."""

from datetime import datetime
from typing import Any

import boto3


def sanitize_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Remove None values from dictionary (simplified approach)."""
    return {k: v for k, v in data.items() if v is not None}


def validate_aws_identifier(identifier: str) -> bool:
    """Simple AWS identifier validation."""
    return bool(
        identifier and len(identifier) > 3 and identifier.replace("-", "").isalnum()
    )


# Note: format_aws_timestamp() function removed - boto3 handles timestamps automatically
# AWS SDK responses include properly formatted timestamps that don't need manual conversion


# Note: chunk_list() function removed - use itertools.batched() directly for Python 3.12+
# For batching: list(itertools.batched(items, chunk_size))


def merge_filters(
    base_filters: dict[str, Any] | None, additional_filters: dict[str, Any] | None
) -> dict[str, Any]:
    """Merge two filter dictionaries."""
    if not base_filters and not additional_filters:
        return {}

    merged = (base_filters or {}).copy()
    merged.update(additional_filters or {})
    return merged


def create_aws_client(profile_name: str, region: str, service_name: str) -> Any:
    """Create boto3 client for AWS service.

    Args:
        profile_name: AWS profile name from ~/.aws/credentials
        region: AWS region (e.g., 'us-east-1', 'eu-west-1')
        service_name: AWS service name (e.g., 'ec2', 's3', 'rds')

    Returns:
        Boto3 client instance
    """
    session = boto3.Session(profile_name=profile_name)
    return session.client(service_name, region_name=region)


def build_params(**kwargs: Any) -> dict[str, Any]:
    """Build parameter dictionary excluding None values.

    Args:
        **kwargs: Parameters to include in the dict

    Returns:
        Dictionary with non-None values
    """
    return {k: v for k, v in kwargs.items() if v is not None}


def format_filters(filters: dict[str, Any] | None) -> list | None:
    """Format filters dictionary to AWS API format.

    Args:
        filters: Dictionary of filter keys and values

    Returns:
        List of filter dictionaries in AWS format
    """
    if not filters:
        return None

    return [
        {"Name": k, "Values": v if isinstance(v, list) else [v]}
        for k, v in filters.items()
    ]


def paginate_results(
    client: Any,
    operation_name: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Handle pagination for AWS API calls using boto3's built-in pagination.

    Args:
        client: Boto3 client instance
        operation_name: Name of the boto3 operation to call
        params: Parameters for the API call

    Returns:
        Combined results from all pages
    """
    paginator = client.get_paginator(operation_name)
    return paginator.paginate(**params).build_full_result()
