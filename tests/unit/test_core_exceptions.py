"""Unit tests for core exceptions."""

import pytest

from aws_mcp_server.core.exceptions import (
    AWSMCPError,
    AWSServiceError,
    InvalidProfileError,
    InvalidRegionError,
    ParameterValidationError,
)


class TestAWSMCPError:
    """Test base AWSMCPError exception."""

    def test_basic_exception(self):
        """Test basic exception creation and inheritance."""
        error = AWSMCPError("Test error message")

        assert isinstance(error, Exception)
        assert str(error) == "Test error message"

    def test_exception_inheritance(self):
        """Test that other exceptions inherit from AWSMCPError."""
        profile_error = InvalidProfileError("test-profile")
        region_error = InvalidRegionError("us-invalid-1")
        service_error = AWSServiceError("ec2", "describe_instances", "API error")
        param_error = ParameterValidationError("region", "Invalid region")

        assert isinstance(profile_error, AWSMCPError)
        assert isinstance(region_error, AWSMCPError)
        assert isinstance(service_error, AWSMCPError)
        assert isinstance(param_error, AWSMCPError)


class TestInvalidProfileError:
    """Test InvalidProfileError exception."""

    def test_profile_error_creation(self):
        """Test InvalidProfileError creation."""
        profile_name = "invalid-profile"
        error = InvalidProfileError(profile_name)

        assert error.profile_name == profile_name
        assert str(error) == f"Invalid or inaccessible AWS profile: {profile_name}"

    def test_profile_error_attributes(self):
        """Test InvalidProfileError attributes."""
        profile_name = "test-profile"
        error = InvalidProfileError(profile_name)

        assert hasattr(error, "profile_name")
        assert error.profile_name == profile_name

    def test_profile_error_with_special_characters(self):
        """Test InvalidProfileError with special characters in profile name."""
        profile_name = "test-profile_123"
        error = InvalidProfileError(profile_name)

        expected_message = f"Invalid or inaccessible AWS profile: {profile_name}"
        assert str(error) == expected_message


class TestInvalidRegionError:
    """Test InvalidRegionError exception."""

    def test_region_error_creation(self):
        """Test InvalidRegionError creation."""
        region = "us-invalid-1"
        error = InvalidRegionError(region)

        assert error.region == region
        assert str(error) == f"Invalid AWS region: {region}"

    def test_region_error_attributes(self):
        """Test InvalidRegionError attributes."""
        region = "eu-fake-1"
        error = InvalidRegionError(region)

        assert hasattr(error, "region")
        assert error.region == region

    def test_region_error_empty_string(self):
        """Test InvalidRegionError with empty string."""
        region = ""
        error = InvalidRegionError(region)

        assert error.region == region
        assert str(error) == "Invalid AWS region: "


class TestAWSServiceError:
    """Test AWSServiceError exception."""

    def test_service_error_creation(self):
        """Test AWSServiceError creation."""
        service = "ec2"
        operation = "describe_instances"
        error_message = "Access denied"

        error = AWSServiceError(service, operation, error_message)

        assert error.service == service
        assert error.operation == operation
        assert error.error_message == error_message

        expected_message = f"AWS {service} {operation} failed: {error_message}"
        assert str(error) == expected_message

    def test_service_error_attributes(self):
        """Test AWSServiceError attributes."""
        service = "s3"
        operation = "list_buckets"
        error_message = "Invalid credentials"

        error = AWSServiceError(service, operation, error_message)

        assert hasattr(error, "service")
        assert hasattr(error, "operation")
        assert hasattr(error, "error_message")

        assert error.service == service
        assert error.operation == operation
        assert error.error_message == error_message

    def test_service_error_complex_message(self):
        """Test AWSServiceError with complex error message."""
        service = "rds"
        operation = "describe_db_instances"
        error_message = "Rate limit exceeded. Retry after 60 seconds."

        error = AWSServiceError(service, operation, error_message)

        expected_message = f"AWS {service} {operation} failed: {error_message}"
        assert str(error) == expected_message


class TestParameterValidationError:
    """Test ParameterValidationError exception."""

    def test_parameter_error_creation(self):
        """Test ParameterValidationError creation."""
        parameter = "instance_id"
        message = "Must start with 'i-'"

        error = ParameterValidationError(parameter, message)

        assert error.parameter == parameter
        assert error.message == message

        expected_message = f"Parameter validation failed for '{parameter}': {message}"
        assert str(error) == expected_message

    def test_parameter_error_attributes(self):
        """Test ParameterValidationError attributes."""
        parameter = "region"
        message = "Invalid region format"

        error = ParameterValidationError(parameter, message)

        assert hasattr(error, "parameter")
        assert hasattr(error, "message")

        assert error.parameter == parameter
        assert error.message == message

    def test_parameter_error_with_quotes(self):
        """Test ParameterValidationError preserves quotes in parameter name."""
        parameter = "bucket-name"
        message = "Contains invalid characters"

        error = ParameterValidationError(parameter, message)

        expected_message = f"Parameter validation failed for '{parameter}': {message}"
        assert str(error) == expected_message

    def test_parameter_error_empty_strings(self):
        """Test ParameterValidationError with empty strings."""
        parameter = ""
        message = ""

        error = ParameterValidationError(parameter, message)

        expected_message = "Parameter validation failed for '': "
        assert str(error) == expected_message


class TestExceptionChaining:
    """Test exception chaining and inheritance."""

    def test_exception_chaining(self):
        """Test that exceptions can be chained."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise AWSServiceError(
                    "ec2", "describe_instances", "Service failed"
                ) from e
        except AWSServiceError as service_error:
            assert service_error.__cause__ is not None
            assert isinstance(service_error.__cause__, ValueError)
            assert str(service_error.__cause__) == "Original error"

    def test_exception_inheritance_chain(self):
        """Test exception inheritance chain."""
        error = InvalidProfileError("test-profile")

        # Test inheritance chain
        assert isinstance(error, InvalidProfileError)
        assert isinstance(error, AWSMCPError)
        assert isinstance(error, Exception)
        assert isinstance(error, BaseException)

    def test_exception_catching(self):
        """Test that specific exceptions can be caught as base exception."""

        def raise_profile_error():
            raise InvalidProfileError("test-profile")

        def raise_region_error():
            raise InvalidRegionError("us-invalid-1")

        # Both should be catchable as AWSMCPError
        with pytest.raises(AWSMCPError):
            raise_profile_error()

        with pytest.raises(AWSMCPError):
            raise_region_error()

        # But also as their specific types
        with pytest.raises(InvalidProfileError):
            raise_profile_error()

        with pytest.raises(InvalidRegionError):
            raise_region_error()
