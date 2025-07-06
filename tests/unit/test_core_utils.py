"""Unit tests for core utilities."""

from datetime import datetime
from unittest.mock import Mock, patch

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
    """Test sanitize_dict function."""

    def test_remove_none_values(self):
        """Test removal of None values."""
        input_dict = {"key1": "value1", "key2": None, "key3": "value3", "key4": None}
        result = sanitize_dict(input_dict)
        expected = {"key1": "value1", "key3": "value3"}
        assert result == expected

    def test_recursive_none_removal(self):
        """Test recursive removal of None values."""
        input_dict = {
            "level1": {
                "key1": "value1",
                "key2": None,
                "level2": {"key3": "value3", "key4": None},
            },
            "key5": None,
        }
        result = sanitize_dict(input_dict)
        expected = {"level1": {"key1": "value1", "level2": {"key3": "value3"}}}
        assert result == expected

    def test_list_handling(self):
        """Test handling of lists with None values."""
        input_dict = {
            "list_key": ["value1", None, "value2", None],
            "nested_list": [{"key1": "value1", "key2": None}, None, {"key3": "value3"}],
        }
        result = sanitize_dict(input_dict)
        expected = {
            "list_key": ["value1", "value2"],
            "nested_list": [{"key1": "value1"}, {"key3": "value3"}],
        }
        assert result == expected

    def test_empty_dict_removal(self):
        """Test removal of empty dictionaries after cleaning."""
        input_dict = {"key1": "value1", "empty_dict": {"key2": None}, "key3": "value3"}
        result = sanitize_dict(input_dict)
        expected = {"key1": "value1", "key3": "value3"}
        assert result == expected

    def test_non_dict_input(self):
        """Test handling of non-dictionary input."""
        assert sanitize_dict("string") == "string"
        assert sanitize_dict(123) == 123
        assert sanitize_dict(None) is None


class TestValidateAWSIdentifier:
    """Test validate_aws_identifier function."""

    def test_valid_instance_ids(self):
        """Test valid EC2 instance IDs."""
        valid_ids = ["i-1234567890abcdef0", "i-12345678", "i-abcdef1234567890a"]
        for instance_id in valid_ids:
            assert validate_aws_identifier(instance_id, "instance_id")

    def test_invalid_instance_ids(self):
        """Test invalid EC2 instance IDs."""
        invalid_ids = [
            "i-",
            "i-12345",  # Too short
            "i-1234567890abcdef0x",  # Too long
            "instance-123",  # Wrong prefix
            "i-xyz",  # Invalid characters
        ]
        for instance_id in invalid_ids:
            assert not validate_aws_identifier(instance_id, "instance_id")

    def test_valid_vpc_ids(self):
        """Test valid VPC IDs."""
        valid_ids = ["vpc-1234567890abcdef0", "vpc-12345678"]
        for vpc_id in valid_ids:
            assert validate_aws_identifier(vpc_id, "vpc_id")

    def test_valid_bucket_names(self):
        """Test valid S3 bucket names."""
        valid_names = [
            "my-bucket",
            "test.bucket.123",
            "a" * 63,  # Max length
            "abc",  # Min length
        ]
        for bucket_name in valid_names:
            assert validate_aws_identifier(bucket_name, "bucket_name")

    def test_invalid_bucket_names(self):
        """Test invalid S3 bucket names."""
        invalid_names = [
            "My-Bucket",  # Uppercase
            "ab",  # Too short
            "a" * 64,  # Too long
            "bucket_with_underscore",  # Underscore not allowed
        ]
        for bucket_name in invalid_names:
            assert not validate_aws_identifier(bucket_name, "bucket_name")

    def test_unknown_identifier_type(self):
        """Test unknown identifier type (should return True)."""
        assert validate_aws_identifier("anything", "unknown_type")


class TestFormatAWSTimestamp:
    """Test format_aws_timestamp function."""

    def test_datetime_input(self):
        """Test datetime input."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        result = format_aws_timestamp(dt)
        assert result == "2024-01-01T12:00:00"

    def test_iso_string_input(self):
        """Test ISO string input."""
        iso_string = "2024-01-01T12:00:00Z"
        result = format_aws_timestamp(iso_string)
        assert result == "2024-01-01T12:00:00+00:00"

    def test_none_input(self):
        """Test None input."""
        assert format_aws_timestamp(None) is None

    def test_invalid_string_input(self):
        """Test invalid string input."""
        invalid_string = "not-a-timestamp"
        result = format_aws_timestamp(invalid_string)
        assert result == invalid_string  # Should return as-is

    def test_other_type_input(self):
        """Test other type input."""
        result = format_aws_timestamp(123456)
        assert result == "123456"


class TestChunkList:
    """Test chunk_list function."""

    def test_basic_chunking(self):
        """Test basic list chunking."""
        items = list(range(10))
        chunks = chunk_list(items, 3)
        expected = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
        assert chunks == expected

    def test_exact_division(self):
        """Test chunking with exact division."""
        items = list(range(9))
        chunks = chunk_list(items, 3)
        expected = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        assert chunks == expected

    def test_empty_list(self):
        """Test chunking empty list."""
        chunks = chunk_list([], 3)
        assert chunks == []

    def test_chunk_size_larger_than_list(self):
        """Test chunk size larger than list."""
        items = [1, 2, 3]
        chunks = chunk_list(items, 10)
        assert chunks == [[1, 2, 3]]

    def test_chunk_size_one(self):
        """Test chunk size of 1."""
        items = [1, 2, 3]
        chunks = chunk_list(items, 1)
        expected = [[1], [2], [3]]
        assert chunks == expected


class TestMergeFilters:
    """Test merge_filters function."""

    def test_merge_two_filters(self):
        """Test merging two filter dictionaries."""
        base = {"key1": "value1", "key2": "value2"}
        additional = {"key3": "value3", "key4": "value4"}
        result = merge_filters(base, additional)
        expected = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
            "key4": "value4",
        }
        assert result == expected

    def test_overlapping_keys(self):
        """Test merging with overlapping keys (additional should override)."""
        base = {"key1": "value1", "key2": "value2"}
        additional = {"key2": "new_value2", "key3": "value3"}
        result = merge_filters(base, additional)
        expected = {"key1": "value1", "key2": "new_value2", "key3": "value3"}
        assert result == expected

    def test_none_inputs(self):
        """Test merging with None inputs."""
        base = {"key1": "value1"}

        # Base is None
        assert merge_filters(None, base) == base

        # Additional is None
        assert merge_filters(base, None) == base

        # Both are None
        assert merge_filters(None, None) == {}

    def test_empty_dictionaries(self):
        """Test merging empty dictionaries."""
        base = {"key1": "value1"}

        result = merge_filters(base, {})
        assert result == base

        result = merge_filters({}, base)
        assert result == base

        result = merge_filters({}, {})
        assert result == {}


class TestCreateAwsClient:
    """Test create_aws_client function."""

    @patch("boto3.Session")
    def test_create_aws_client(self, mock_session):
        """Test create_aws_client function."""
        mock_client = Mock()
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_client
        mock_session.return_value = mock_session_instance

        client = create_aws_client("test-profile", "us-east-1", "ec2")

        assert client == mock_client
        mock_session.assert_called_once_with(profile_name="test-profile")
        mock_session_instance.client.assert_called_once_with(
            "ec2", region_name="us-east-1"
        )


class TestBuildParams:
    """Test build_params function."""

    def test_build_params(self):
        """Test build_params function."""
        params = build_params(key1="value1", key2=None, key3="value3", key4=None)

        expected = {"key1": "value1", "key3": "value3"}
        assert params == expected

    def test_build_params_empty(self):
        """Test build_params with empty input."""
        params = build_params()
        assert params == {}

    def test_build_params_all_none(self):
        """Test build_params with all None values."""
        params = build_params(key1=None, key2=None)
        assert params == {}


class TestFormatFilters:
    """Test format_filters function."""

    def test_format_filters_none(self):
        """Test format_filters with None input."""
        result = format_filters(None)
        assert result is None

    def test_format_filters_empty(self):
        """Test format_filters with empty dict."""
        result = format_filters({})
        assert result is None

    def test_format_filters_dict(self):
        """Test format_filters with dictionary input."""
        filters = {
            "instance-state-name": ["running", "stopped"],
            "instance-type": "t2.micro",
            "tag:Environment": "production",
        }

        result = format_filters(filters)
        expected = [
            {"Name": "instance-state-name", "Values": ["running", "stopped"]},
            {"Name": "instance-type", "Values": ["t2.micro"]},
            {"Name": "tag:Environment", "Values": ["production"]},
        ]

        assert result == expected

    def test_format_filters_single_values(self):
        """Test format_filters with single values converted to lists."""
        filters = {"single-value": "test"}
        result = format_filters(filters)
        expected = [{"Name": "single-value", "Values": ["test"]}]

        assert result == expected


class TestPaginateResults:
    """Test paginate_results function."""

    def test_paginate_results(self):
        """Test paginate_results function."""
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

        params = {"MaxResults": 10}
        result = paginate_results(mock_client, "describe_items", params)

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

    def test_paginate_results_single_page(self):
        """Test paginate_results with single page."""
        mock_paginator = Mock()
        mock_client = Mock()
        mock_client.get_paginator.return_value = mock_paginator

        page = {"Items": [{"id": 1}], "Metadata": {"RequestId": "req1"}}
        mock_paginator.paginate.return_value = [page]

        result = paginate_results(mock_client, "describe_items", {})

        # Should return the single page as-is
        assert result == page

    def test_paginate_results_non_list_merge(self):
        """Test paginate_results with non-list values."""
        mock_paginator = Mock()
        mock_client = Mock()
        mock_client.get_paginator.return_value = mock_paginator

        page1 = {"Count": 5, "Items": [{"id": 1}]}
        page2 = {
            "Count": 3,  # This should not be merged
            "Items": [{"id": 2}],
        }
        mock_paginator.paginate.return_value = [page1, page2]

        result = paginate_results(mock_client, "describe_items", {})

        # Count should come from first page, Items should be merged
        expected = {"Count": 5, "Items": [{"id": 1}, {"id": 2}]}
        assert result == expected
