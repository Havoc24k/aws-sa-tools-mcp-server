"""Base classes for AWS MCP tools."""

from abc import ABC, abstractmethod
from typing import Any

import boto3


class AWSService(ABC):
    """Base class for AWS service implementations."""

    def __init__(self, profile_name: str, region: str):
        """Initialize AWS service with session and client.

        Args:
            profile_name: AWS profile name from ~/.aws/credentials
            region: AWS region (e.g., 'us-east-1', 'eu-west-1')
        """
        self.profile_name = profile_name
        self.region = region
        self.session = boto3.Session(profile_name=profile_name)
        self.client = self._create_client()

    @property
    @abstractmethod
    def service_name(self) -> str:
        """Return the AWS service name for boto3 client creation."""
        pass

    def _create_client(self):
        """Create boto3 client for the service."""
        return self.session.client(self.service_name, region_name=self.region)

    def _build_params(self, **kwargs) -> dict[str, Any]:
        """Build parameter dictionary excluding None values.

        Args:
            **kwargs: Parameters to include in the dict

        Returns:
            Dictionary with non-None values
        """
        return {k: v for k, v in kwargs.items() if v is not None}

    def _format_filters(self, filters: dict[str, Any] | None) -> list | None:
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


class PaginatedAWSService(AWSService):
    """Base class for AWS services that support pagination."""

    def _paginate_results(
        self,
        operation_name: str,
        params: dict[str, Any],
        max_results_key: str = "MaxResults",
        next_token_key: str = "NextToken",
    ) -> dict[str, Any]:
        """Handle pagination for AWS API calls.

        Args:
            operation_name: Name of the boto3 operation to call
            params: Parameters for the API call
            max_results_key: Key name for max results parameter
            next_token_key: Key name for next token parameter

        Returns:
            Combined results from all pages
        """
        paginator = self.client.get_paginator(operation_name)
        pages = paginator.paginate(**params)

        # Combine all pages into a single result
        combined_result = {}
        for page in pages:
            if not combined_result:
                combined_result = page.copy()
            else:
                # Merge results - this is service-specific but works for most cases
                for key, value in page.items():
                    if isinstance(value, list):
                        if key in combined_result:
                            combined_result[key].extend(value)
                        else:
                            combined_result[key] = value
                    elif key not in combined_result:
                        combined_result[key] = value

        return combined_result
