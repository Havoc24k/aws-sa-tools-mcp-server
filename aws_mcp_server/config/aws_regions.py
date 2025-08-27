"""AWS region utilities using boto3 dynamic discovery."""

from functools import lru_cache

import boto3


@lru_cache(maxsize=1)
def get_all_regions() -> set[str]:
    """Get all available AWS regions using boto3.

    Returns:
        Set of all AWS region codes
    """
    try:
        session = boto3.Session()
        return set(session.get_available_regions('ec2'))
    except Exception:
        # Fallback to common regions if boto3 call fails
        return {
            "us-east-1", "us-east-2", "us-west-1", "us-west-2",
            "eu-west-1", "eu-west-2", "eu-central-1", "eu-north-1",
            "ap-south-1", "ap-southeast-1", "ap-southeast-2",
            "ap-northeast-1", "ap-northeast-2", "sa-east-1", "ca-central-1"
        }


def is_valid_region(region: str) -> bool:
    """Check if a region code is valid using boto3.

    Args:
        region: AWS region code to validate

    Returns:
        True if region is valid, False otherwise
    """
    return region in get_all_regions()


def get_regions_by_prefix(prefix: str) -> list[str]:
    """Get regions that start with a specific prefix.

    Args:
        prefix: Region prefix (e.g., 'us', 'eu', 'ap')

    Returns:
        List of region codes with the prefix
    """
    return sorted([r for r in get_all_regions() if r.startswith(prefix)])
