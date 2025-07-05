"""AWS region configurations and utilities."""

from typing import Dict, List, Set

# AWS regions organized by geographic area
AWS_REGIONS = {
    "us": {
        "us-east-1": {"name": "N. Virginia", "availability_zones": 6},
        "us-east-2": {"name": "Ohio", "availability_zones": 3},
        "us-west-1": {"name": "N. California", "availability_zones": 3},
        "us-west-2": {"name": "Oregon", "availability_zones": 4},
    },
    "eu": {
        "eu-west-1": {"name": "Ireland", "availability_zones": 3},
        "eu-west-2": {"name": "London", "availability_zones": 3},
        "eu-west-3": {"name": "Paris", "availability_zones": 3},
        "eu-central-1": {"name": "Frankfurt", "availability_zones": 3},
        "eu-north-1": {"name": "Stockholm", "availability_zones": 3},
        "eu-south-1": {"name": "Milan", "availability_zones": 3},
    },
    "ap": {
        "ap-south-1": {"name": "Mumbai", "availability_zones": 3},
        "ap-southeast-1": {"name": "Singapore", "availability_zones": 3},
        "ap-southeast-2": {"name": "Sydney", "availability_zones": 3},
        "ap-northeast-1": {"name": "Tokyo", "availability_zones": 4},
        "ap-northeast-2": {"name": "Seoul", "availability_zones": 4},
        "ap-northeast-3": {"name": "Osaka", "availability_zones": 3},
        "ap-east-1": {"name": "Hong Kong", "availability_zones": 3},
    },
    "other": {
        "sa-east-1": {"name": "São Paulo", "availability_zones": 3},
        "ca-central-1": {"name": "Canada Central", "availability_zones": 3},
        "me-south-1": {"name": "Bahrain", "availability_zones": 3},
        "af-south-1": {"name": "Cape Town", "availability_zones": 3},
    },
}


def get_all_regions() -> set[str]:
    """Get all available AWS regions.

    Returns:
        Set of all AWS region codes
    """
    regions = set()
    for area_regions in AWS_REGIONS.values():
        regions.update(area_regions.keys())
    return regions


def get_regions_by_area(area: str) -> list[str]:
    """Get regions for a specific geographic area.

    Args:
        area: Geographic area ('us', 'eu', 'ap', 'other')

    Returns:
        List of region codes for the area
    """
    return list(AWS_REGIONS.get(area, {}).keys())


def get_region_info(region: str) -> dict[str, any]:
    """Get information about a specific region.

    Args:
        region: AWS region code

    Returns:
        Dictionary with region information
    """
    for area_regions in AWS_REGIONS.values():
        if region in area_regions:
            return area_regions[region]
    return {}


def is_valid_region(region: str) -> bool:
    """Check if a region code is valid.

    Args:
        region: AWS region code to validate

    Returns:
        True if region is valid, False otherwise
    """
    return region in get_all_regions()


def get_nearest_regions(region: str) -> list[str]:
    """Get geographically nearest regions to a given region.

    Args:
        region: Base region code

    Returns:
        List of nearest region codes
    """
    # Find which area the region belongs to
    for _area, area_regions in AWS_REGIONS.items():
        if region in area_regions:
            # Return other regions in the same area
            return [r for r in area_regions.keys() if r != region]

    return []
