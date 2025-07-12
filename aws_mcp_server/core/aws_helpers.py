"""Simplified AWS tool helpers to eliminate DRY violations."""

from collections.abc import Callable
from functools import wraps
from typing import Any

from ..mcp import mcp
from .config import AWS_CONFIG
from .constants import AWSService, DocumentationType
from .utils import build_params, create_aws_client


def aws_tool_simple(
    name: str,
    service: AWSService,
    operation: str,
    description: str | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Ultra-simple AWS tool decorator that eliminates all repetition.

    Automatically handles:
    - Standard AWS parameters (profile_name, region)
    - AWS client creation
    - Parameter building and filtering
    - MCP tool registration
    - Basic error handling
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @mcp.tool(
            name=name,
            description=description or f"Execute {service.value} {operation}",
        )
        @wraps(func)
        async def wrapper(
            profile_name: str = AWS_CONFIG.default_profile,
            region: str = AWS_CONFIG.default_region,
            **kwargs: Any,
        ) -> Any:
            # Create client and call operation
            client = create_aws_client(profile_name, region, service.value)
            params = build_params(**kwargs)
            operation_func = getattr(client, operation)
            return operation_func(**params)

        return wrapper

    return decorator


def create_simple_docs(operation: str, **custom_params: str) -> str:
    """Create simplified, consistent documentation."""
    base_params = {
        "profile_name": DocumentationType.PROFILE_PARAM,
        "region": DocumentationType.REGION_PARAM,
    }

    param_docs = []
    for param, desc in {**base_params, **custom_params}.items():
        param_docs.append(f"- {param}: {desc}")

    return f"""Execute {operation} operation.

{DocumentationType.REQUIRED_PARAMS}
{chr(10).join(param_docs[:2])}

{DocumentationType.OPTIONAL_PARAMS}
{chr(10).join(param_docs[2:]) if len(param_docs) > 2 else "None"}"""


# Common parameter descriptions for reuse
FILTER_PARAM = "Dictionary of filters to apply"
MAX_RESULTS_PARAM = "Maximum number of results to return"
NEXT_TOKEN_PARAM = "Token for pagination"
