"""Utility functions for AWS MCP server."""

from typing import Any, Dict, List, Optional
import re
from datetime import datetime


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from a dictionary recursively.
    
    Args:
        data: Dictionary to sanitize
        
    Returns:
        Dictionary with None values removed
    """
    if not isinstance(data, dict):
        return data
    
    cleaned = {}
    for key, value in data.items():
        if value is None:
            continue
        elif isinstance(value, dict):
            cleaned_value = sanitize_dict(value)
            if cleaned_value:  # Only add if not empty after cleaning
                cleaned[key] = cleaned_value
        elif isinstance(value, list):
            cleaned_list = [sanitize_dict(item) if isinstance(item, dict) else item 
                          for item in value if item is not None]
            if cleaned_list:
                cleaned[key] = cleaned_list
        else:
            cleaned[key] = value
    
    return cleaned


def validate_aws_identifier(identifier: str, identifier_type: str) -> bool:
    """Validate AWS resource identifier format.
    
    Args:
        identifier: The identifier to validate
        identifier_type: Type of identifier (e.g., 'instance_id', 'vpc_id', 'bucket_name')
        
    Returns:
        True if identifier is valid format, False otherwise
    """
    patterns = {
        'instance_id': r'^i-[0-9a-f]{8,17}$',
        'vpc_id': r'^vpc-[0-9a-f]{8,17}$',
        'subnet_id': r'^subnet-[0-9a-f]{8,17}$',
        'security_group_id': r'^sg-[0-9a-f]{8,17}$',
        'bucket_name': r'^[a-z0-9.\-]{3,63}$',
        'db_instance_identifier': r'^[a-zA-Z][a-zA-Z0-9\-]{0,62}$'
    }
    
    pattern = patterns.get(identifier_type)
    if not pattern:
        return True  # Unknown type, assume valid
    
    return bool(re.match(pattern, identifier))


def format_aws_timestamp(timestamp: Any) -> Optional[str]:
    """Format AWS timestamp to ISO string.
    
    Args:
        timestamp: AWS timestamp (datetime or string)
        
    Returns:
        ISO formatted timestamp string or None
    """
    if timestamp is None:
        return None
    
    if isinstance(timestamp, datetime):
        return timestamp.isoformat()
    
    if isinstance(timestamp, str):
        try:
            # Try to parse and reformat
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.isoformat()
        except ValueError:
            return timestamp
    
    return str(timestamp)


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size.
    
    Args:
        items: List to chunk
        chunk_size: Maximum size of each chunk
        
    Returns:
        List of chunked lists
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def merge_filters(base_filters: Optional[Dict[str, Any]], 
                 additional_filters: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Merge two filter dictionaries.
    
    Args:
        base_filters: Base filter dictionary
        additional_filters: Additional filters to merge
        
    Returns:
        Merged filter dictionary
    """
    if not base_filters and not additional_filters:
        return {}
    
    if not base_filters:
        return additional_filters or {}
    
    if not additional_filters:
        return base_filters
    
    merged = base_filters.copy()
    merged.update(additional_filters)
    return merged