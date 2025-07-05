"""Unit tests for core base classes."""

from unittest.mock import Mock, patch

import pytest

from aws_mcp_server.core.base import AWSService, PaginatedAWSService


class ConcreteAWSService(AWSService):
    """Concrete implementation for testing."""

    @property
    def service_name(self) -> str:
        return "test-service"


class ConcretePaginatedAWSService(PaginatedAWSService):
    """Concrete paginated implementation for testing."""

    @property
    def service_name(self) -> str:
        return "test-paginated-service"


class TestAWSService:
    """Test AWSService base class."""

    @patch("boto3.Session")
    def test_initialization(self, mock_session):
        """Test service initialization."""
        mock_client = Mock()
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_client
        mock_session.return_value = mock_session_instance

        service = ConcreteAWSService("test-profile", "us-east-1")

        assert service.profile_name == "test-profile"
        assert service.region == "us-east-1"
        assert service.session == mock_session_instance
        assert service.client == mock_client

        mock_session.assert_called_once_with(profile_name="test-profile")
        mock_session_instance.client.assert_called_once_with(
            "test-service", region_name="us-east-1"
        )

    def test_build_params(self):
        """Test _build_params method."""
        with patch("boto3.Session"):
            service = ConcreteAWSService("test-profile", "us-east-1")

            params = service._build_params(
                key1="value1", key2=None, key3="value3", key4=None
            )

            expected = {"key1": "value1", "key3": "value3"}
            assert params == expected

    def test_format_filters_none(self):
        """Test _format_filters with None input."""
        with patch("boto3.Session"):
            service = ConcreteAWSService("test-profile", "us-east-1")
            result = service._format_filters(None)
            assert result is None

    def test_format_filters_dict(self):
        """Test _format_filters with dictionary input."""
        with patch("boto3.Session"):
            service = ConcreteAWSService("test-profile", "us-east-1")

            filters = {
                "instance-state-name": ["running", "stopped"],
                "instance-type": "t2.micro",
                "tag:Environment": "production",
            }

            result = service._format_filters(filters)
            expected = [
                {"Name": "instance-state-name", "Values": ["running", "stopped"]},
                {"Name": "instance-type", "Values": ["t2.micro"]},
                {"Name": "tag:Environment", "Values": ["production"]},
            ]

            assert result == expected

    def test_format_filters_single_values(self):
        """Test _format_filters with single values converted to lists."""
        with patch("boto3.Session"):
            service = ConcreteAWSService("test-profile", "us-east-1")

            filters = {"single-value": "test"}
            result = service._format_filters(filters)
            expected = [{"Name": "single-value", "Values": ["test"]}]

            assert result == expected


class TestPaginatedAWSService:
    """Test PaginatedAWSService base class."""

    @patch("boto3.Session")
    def test_initialization(self, mock_session):
        """Test paginated service initialization."""
        mock_client = Mock()
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_client
        mock_session.return_value = mock_session_instance

        service = ConcretePaginatedAWSService("test-profile", "us-east-1")

        assert service.profile_name == "test-profile"
        assert service.region == "us-east-1"
        assert service.client == mock_client

    @patch("boto3.Session")
    def test_paginate_results(self, mock_session):
        """Test _paginate_results method."""
        # Mock paginator and pages
        mock_paginator = Mock()
        mock_client = Mock()
        mock_client.get_paginator.return_value = mock_paginator

        # Mock pages with different data structures
        page1 = {
            "Items": [{"id": 1}, {"id": 2}],
            "NextToken": "token1",
            "Metadata": {"RequestId": "req1"},
        }
        page2 = {"Items": [{"id": 3}, {"id": 4}], "Metadata": {"RequestId": "req2"}}
        mock_paginator.paginate.return_value = [page1, page2]

        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_client
        mock_session.return_value = mock_session_instance

        service = ConcretePaginatedAWSService("test-profile", "us-east-1")

        params = {"MaxResults": 10}
        result = service._paginate_results("describe_items", params)

        # Verify paginator was called correctly
        mock_client.get_paginator.assert_called_once_with("describe_items")
        mock_paginator.paginate.assert_called_once_with(**params)

        # Verify results were combined correctly
        expected = {
            "Items": [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}],
            "NextToken": "token1",  # From first page
            "Metadata": {"RequestId": "req1"},  # From first page
        }
        assert result == expected

    @patch("boto3.Session")
    def test_paginate_results_single_page(self, mock_session):
        """Test _paginate_results with single page."""
        mock_paginator = Mock()
        mock_client = Mock()
        mock_client.get_paginator.return_value = mock_paginator

        page = {"Items": [{"id": 1}], "Metadata": {"RequestId": "req1"}}
        mock_paginator.paginate.return_value = [page]

        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_client
        mock_session.return_value = mock_session_instance

        service = ConcretePaginatedAWSService("test-profile", "us-east-1")

        result = service._paginate_results("describe_items", {})

        # Should return the single page as-is
        assert result == page

    @patch("boto3.Session")
    def test_paginate_results_non_list_merge(self, mock_session):
        """Test _paginate_results with non-list values."""
        mock_paginator = Mock()
        mock_client = Mock()
        mock_client.get_paginator.return_value = mock_paginator

        page1 = {"Count": 5, "Items": [{"id": 1}]}
        page2 = {
            "Count": 3,  # This should not be merged
            "Items": [{"id": 2}],
        }
        mock_paginator.paginate.return_value = [page1, page2]

        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_client
        mock_session.return_value = mock_session_instance

        service = ConcretePaginatedAWSService("test-profile", "us-east-1")

        result = service._paginate_results("describe_items", {})

        # Count should come from first page, Items should be merged
        expected = {"Count": 5, "Items": [{"id": 1}, {"id": 2}]}
        assert result == expected
