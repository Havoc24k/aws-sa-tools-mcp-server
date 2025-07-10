"""Modern AWS tool decorator to eliminate DRY violations."""

from collections.abc import Callable
from functools import wraps
from typing import Any

from ..mcp import mcp
from .utils import build_params, create_aws_client


def aws_tool(
    name: str,
    description: str,
    service_name: str,
) -> Callable[[Callable], Callable]:
    """
    Modern decorator for AWS service tools that eliminates DRY violations.

    Automatically handles:
    - Standard AWS parameters (profile_name, region)
    - AWS client creation
    - Parameter building
    - MCP tool registration
    """

    def decorator(func: Callable) -> Callable:
        @mcp.tool(name=name, description=description)
        @wraps(func)
        async def wrapper(profile_name: str, region: str, **kwargs: Any) -> Any:
            # Automatically create AWS client
            client = create_aws_client(profile_name, region, service_name)

            # Call the original function with client and cleaned parameters
            params = build_params(**kwargs)
            return await func(client, params)

        return wrapper

    return decorator
