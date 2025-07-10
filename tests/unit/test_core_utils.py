"""Unit tests for simplified core utilities."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from aws_mcp_server.core.utils import (
    build_params,
    chunk_list,
    create_aws_client,
    format_aws_timestamp,
    format_filters,
    merge_filters,
    paginate_results,
    sanitize_dict,
    validate_aws_identifier,
)


class TestSanitizeDict:
    """Test simplified sanitize_dict function."""

    def test_remove_none_values(self):
        """Test basic removal of None values."""
        input_dict = {"key1": "value1", "key2": None, "key3": "value3"}
        result = sanitize_dict(input_dict)
        expected = {"key1": "value1", "key3": "value3"}
        assert result == expected

    def test_empty_dict_handling(self):
        """Test handling of empty dictionary."""
        input_dict = {}
        result = sanitize_dict(input_dict)
        assert result == {}

    def test_all_none_values(self):
        """Test dictionary with all None values."""
        input_dict = {"key1": None, "key2": None}
        result = sanitize_dict(input_dict)
        assert result == {}

    def test_mixed_values(self):
        """Test dictionary with mixed value types."""
        input_dict = {
            "string": "value",
            "number": 42,
            "none_val": None,
            "boolean": True,
            "list": [1, 2, 3],
        }
        result = sanitize_dict(input_dict)
        expected = {
            "string": "value",
            "number": 42,
            "boolean": True,
            "list": [1, 2, 3],
        }
        assert result == expected


class TestValidateAWSIdentifier:
    """Test simplified validate_aws_identifier function."""

    def test_valid_identifiers(self):
        """Test valid AWS identifiers."""
        assert validate_aws_identifier("i-1234567890abcdef0") is True
        assert validate_aws_identifier("vpc-12345678") is True
        assert validate_aws_identifier("sg-1234abcd") is True
        assert validate_aws_identifier("subnet-12345678") is True
        assert validate_aws_identifier("my-bucket-name") is True

    def test_invalid_identifiers(self):
        """Test invalid AWS identifiers."""
        assert validate_aws_identifier("") is False
        assert validate_aws_identifier("ab") is False  # Too short
        assert validate_aws_identifier("abc") is False  # Still too short
        assert validate_aws_identifier("test@#$") is False  # Invalid characters

    def test_edge_cases(self):
        """Test edge cases."""
        assert validate_aws_identifier("abcd") is True  # Minimum length
        assert validate_aws_identifier("test-123") is True  # With dash
        assert validate_aws_identifier("test_123") is False  # Underscore not alphanumeric


class TestFormatAWSTimestamp:
    """Test format_aws_timestamp function with pattern matching."""

    def test_none_input(self):
        """Test None input returns None."""
        assert format_aws_timestamp(None) is None

    def test_datetime_input(self):
        """Test datetime input."""
        dt = datetime(2023, 1, 1, 12, 0, 0)
        result = format_aws_timestamp(dt)
        assert result == "2023-01-01T12:00:00"

    def test_iso_string_input(self):
        """Test ISO string input."""
        iso_string = "2023-01-01T12:00:00"
        result = format_aws_timestamp(iso_string)
        assert result == "2023-01-01T12:00:00"

    def test_utc_string_input(self):
        """Test UTC string with Z suffix."""
        utc_string = "2023-01-01T12:00:00Z"
        result = format_aws_timestamp(utc_string)
        assert result == "2023-01-01T12:00:00+00:00"

    def test_invalid_string_input(self):
        """Test invalid string input."""
        invalid_string = "not-a-date"
        result = format_aws_timestamp(invalid_string)
        assert result == "not-a-date"

    def test_other_input_types(self):
        """Test other input types."""
        assert format_aws_timestamp(123) == "123"
        assert format_aws_timestamp(12.34) == "12.34"


class TestMergeFilters:
    """Test simplified merge_filters function."""

    def test_both_empty(self):
        """Test merging when both filters are empty."""
        result = merge_filters(None, None)
        assert result == {}

    def test_base_empty(self):
        """Test merging when base is empty."""
        additional = {"key1": "value1"}
        result = merge_filters(None, additional)
        assert result == additional

    def test_additional_empty(self):
        """Test merging when additional is empty."""
        base = {"key1": "value1"}
        result = merge_filters(base, None)
        assert result == base

    def test_merge_different_keys(self):
        """Test merging filters with different keys."""
        base = {"key1": "value1"}
        additional = {"key2": "value2"}
        result = merge_filters(base, additional)
        expected = {"key1": "value1", "key2": "value2"}
        assert result == expected

    def test_merge_overlapping_keys(self):
        """Test merging filters with overlapping keys."""
        base = {"key1": "value1", "key2": "value2"}
        additional = {"key2": "new_value2", "key3": "value3"}
        result = merge_filters(base, additional)
        expected = {"key1": "value1", "key2": "new_value2", "key3": "value3"}
        assert result == expected


class TestPaginateResults:
    """Test simplified paginate_results function."""

    def test_paginate_results_success(self):
        """Test successful pagination with build_full_result."""
        mock_client = Mock()
        mock_paginator = Mock()
        mock_page_iterator = Mock()

        mock_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = mock_page_iterator
        mock_page_iterator.build_full_result.return_value = {"Items": [{"id": 1}, {"id": 2}]}

        result = paginate_results(mock_client, "describe_items", {"MaxItems": 10})

        assert result == {"Items": [{"id": 1}, {"id": 2}]}
        mock_client.get_paginator.assert_called_once_with("describe_items")
        mock_paginator.paginate.assert_called_once_with(MaxItems=10)
        mock_page_iterator.build_full_result.assert_called_once()


class TestBuildParams:
    """Test build_params function."""

    def test_remove_none_values(self):
        """Test removal of None values from parameters."""
        result = build_params(key1="value1", key2=None, key3="value3")
        expected = {"key1": "value1", "key3": "value3"}
        assert result == expected

    def test_empty_params(self):
        """Test with no parameters."""
        result = build_params()
        assert result == {}

    def test_all_none_params(self):
        """Test with all None parameters."""
        result = build_params(key1=None, key2=None)
        assert result == {}


class TestFormatFilters:
    """Test format_filters function."""

    def test_none_filters(self):
        """Test with None filters."""
        result = format_filters(None)
        assert result is None

    def test_empty_filters(self):
        """Test with empty filters dictionary."""
        result = format_filters({})
        assert result is None

    def test_single_filter(self):
        """Test with single filter."""
        filters = {"instance-state-name": "running"}
        result = format_filters(filters)
        expected = [{"Name": "instance-state-name", "Values": ["running"]}]
        assert result == expected

    def test_multiple_filters(self):
        """Test with multiple filters."""
        filters = {"instance-state-name": "running", "instance-type": "t2.micro"}
        result = format_filters(filters)
        expected = [
            {"Name": "instance-state-name", "Values": ["running"]},
            {"Name": "instance-type", "Values": ["t2.micro"]},
        ]
        assert result == expected

    def test_list_values(self):
        """Test with list values."""
        filters = {"instance-state-name": ["running", "stopped"]}
        result = format_filters(filters)
        expected = [{"Name": "instance-state-name", "Values": ["running", "stopped"]}]
        assert result == expected


class TestChunkList:
    """Test chunk_list function."""

    def test_simple_chunk(self):
        """Test chunking a simple list."""
        items = [1, 2, 3, 4, 5]
        result = chunk_list(items, 2)
        expected = [[1, 2], [3, 4], [5]]
        assert result == expected

    def test_exact_chunks(self):
        """Test when list divides evenly into chunks."""
        items = [1, 2, 3, 4]
        result = chunk_list(items, 2)
        expected = [[1, 2], [3, 4]]
        assert result == expected

    def test_empty_list(self):
        """Test with empty list."""
        result = chunk_list([], 2)
        assert result == []

    def test_single_item(self):
        """Test with single item."""
        result = chunk_list([1], 2)
        assert result == [[1]]


class TestCreateAWSClient:
    """Test create_aws_client function."""

    def test_client_creation(self):
        """Test AWS client creation."""
        # This test would require mocking boto3.Session
        # For now, just test that the function exists and has correct signature
        assert callable(create_aws_client)

        # We can't easily test this without mocking boto3
        # but we can verify the function signature
        import inspect
        sig = inspect.signature(create_aws_client)
        expected_params = ["profile_name", "region", "service_name"]
        actual_params = list(sig.parameters.keys())
        assert actual_params == expected_params
