"""Unit tests for core exceptions."""

import pytest

from aws_mcp_server.core.exceptions import AWSMCPError


class TestAWSMCPError:
    """Test simplified AWSMCPError exception."""

    def test_basic_exception(self):
        """Test basic exception creation and inheritance."""
        error = AWSMCPError("Test error message")

        assert isinstance(error, Exception)
        assert str(error) == "Test error message"

    def test_exception_with_empty_message(self):
        """Test exception with empty message."""
        error = AWSMCPError("")
        assert str(error) == ""

    def test_exception_inheritance(self):
        """Test exception inheritance from base Exception."""
        error = AWSMCPError("Test message")

        assert isinstance(error, AWSMCPError)
        assert isinstance(error, Exception)
        assert isinstance(error, BaseException)


class TestExceptionUsage:
    """Test exception usage patterns."""

    def test_exception_chaining(self):
        """Test that exceptions can be chained."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise AWSMCPError("Service failed") from e
        except AWSMCPError as service_error:
            assert service_error.__cause__ is not None
            assert isinstance(service_error.__cause__, ValueError)
            assert str(service_error.__cause__) == "Original error"

    def test_exception_catching(self):
        """Test that AWSMCPError can be caught properly."""

        def raise_aws_error():
            raise AWSMCPError("AWS operation failed")

        with pytest.raises(AWSMCPError):
            raise_aws_error()

        with pytest.raises(Exception):
            raise_aws_error()

    def test_exception_with_detailed_message(self):
        """Test exception with detailed error message."""
        detailed_message = "AWS EC2 describe_instances failed: Access denied for profile 'test-profile' in region 'us-east-1'"
        error = AWSMCPError(detailed_message)

        assert str(error) == detailed_message
