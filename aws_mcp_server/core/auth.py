"""AWS authentication utilities."""

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
        return list(session.available_profiles)
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
        region = session.region_name
        return region if region is not None else None
    except Exception:
        return None


def validate_region(region: str) -> bool:
    """Validate AWS region using boto3's built-in region discovery.

    Args:
        region: AWS region to validate

    Returns:
        True if region is valid, False otherwise
    """
    try:
        return region in boto3.Session().get_available_regions("ec2")
    except Exception:
        # Fallback to common regions if boto3 call fails
        common_regions = {
            "us-east-1",
            "us-east-2",
            "us-west-1",
            "us-west-2",
            "eu-west-1",
            "eu-central-1",
            "ap-southeast-1",
            "ap-northeast-1",
        }
        return region in common_regions
