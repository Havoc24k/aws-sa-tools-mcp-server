"""Unit tests for core utilities."""

from datetime import datetime

import pytest

from aws_mcp_server.core.utils import (
    chunk_list,
    format_aws_timestamp,
    merge_filters,
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
