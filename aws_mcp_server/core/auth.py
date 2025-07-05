"""AWS authentication utilities."""

import os
from typing import List, Optional

import boto3


def validate_aws_profile(profile_name: str) -> bool:
    """Validate that an AWS profile exists and is accessible.

    Args:
        profile_name: AWS profile name to validate

    Returns:
        True if profile is valid, False otherwise
    """
    try:
        session = boto3.Session(profile_name=profile_name)
        # Try to get caller identity to validate credentials
        sts = session.client("sts")
        sts.get_caller_identity()
        return True
    except Exception:
        return False


def list_available_profiles() -> list[str]:
    """List all available AWS profiles.

    Returns:
        List of profile names
    """
    try:
        session = boto3.Session()
        return session.available_profiles
    except Exception:
        return []


def get_default_region(profile_name: str | None = None) -> str | None:
    """Get default region for a profile.

    Args:
        profile_name: AWS profile name (uses default if None)

    Returns:
        Default region or None if not configured
    """
    try:
        session = boto3.Session(profile_name=profile_name)
        return session.region_name
    except Exception:
        return None


def validate_region(region: str) -> bool:
    """Validate that a region is a valid AWS region.

    Args:
        region: AWS region to validate

    Returns:
        True if region is valid, False otherwise
    """
    # List of AWS regions (simplified - in practice you might want to fetch this dynamically)
    valid_regions = {
        "us-east-1",
        "us-east-2",
        "us-west-1",
        "us-west-2",
        "eu-west-1",
        "eu-west-2",
        "eu-west-3",
        "eu-central-1",
        "eu-north-1",
        "ap-south-1",
        "ap-southeast-1",
        "ap-southeast-2",
        "ap-northeast-1",
        "ap-northeast-2",
        "sa-east-1",
        "ca-central-1",
        "ap-east-1",
        "me-south-1",
        "af-south-1",
    }
    return region in valid_regions
