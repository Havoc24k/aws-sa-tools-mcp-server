"""Global pytest configuration and fixtures."""

import os
from collections.abc import Generator
from typing import Any
from unittest.mock import Mock, patch

import boto3
import pytest
from moto import mock_aws

# Disable AWS credential checks for testing
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up global test environment."""
    # Ensure we're in test mode
    os.environ["TESTING"] = "true"
    yield
    # Cleanup
    os.environ.pop("TESTING", None)


@pytest.fixture
def aws_credentials():
    """Mock AWS credentials for testing."""
    return {
        "profile_name": "test",
        "region": "us-east-1",
        "access_key_id": "testing",
        "secret_access_key": "testing",
    }


@pytest.fixture
def mock_boto3_session():
    """Mock boto3 session."""
    with patch("boto3.Session") as mock_session:
        mock_instance = Mock()
        mock_session.return_value = mock_instance
        yield mock_instance


# AWS Service Mocks
@pytest.fixture
def mock_aws_services():
    """Mock all AWS services using moto's unified mock_aws."""
    with mock_aws():
        yield


# Test data fixtures
@pytest.fixture
def sample_ec2_instance():
    """Sample EC2 instance data."""
    return {
        "InstanceId": "i-1234567890abcdef0",
        "ImageId": "ami-12345678",
        "State": {"Name": "running"},
        "InstanceType": "t2.micro",
        "KeyName": "my-key",
        "VpcId": "vpc-12345678",
        "SubnetId": "subnet-12345678",
        "Tags": [
            {"Key": "Name", "Value": "test-instance"},
            {"Key": "Environment", "Value": "testing"},
        ],
    }


@pytest.fixture
def sample_s3_bucket():
    """Sample S3 bucket data."""
    return {"Name": "test-bucket", "CreationDate": "2024-01-01T00:00:00.000Z"}


@pytest.fixture
def sample_rds_instance():
    """Sample RDS instance data."""
    return {
        "DBInstanceIdentifier": "test-db",
        "DBInstanceClass": "db.t3.micro",
        "Engine": "mysql",
        "EngineVersion": "8.0.35",
        "DBInstanceStatus": "available",
        "MasterUsername": "admin",
        "AllocatedStorage": 20,
    }


# FastMCP testing fixtures
@pytest.fixture
def mcp_server():
    """FastMCP server instance for testing."""
    from aws_mcp_server.mcp import mcp

    return mcp


# Utility functions for tests
def create_mock_aws_response(service: str, operation: str, **kwargs) -> dict[str, Any]:
    """Create a mock AWS response."""
    base_response = {
        "ResponseMetadata": {
            "RequestId": "test-request-id",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {},
            "RetryAttempts": 0,
        }
    }
    base_response.update(kwargs)
    return base_response


def assert_mcp_tool_response(response, expected_type: str = "text"):
    """Assert MCP tool response format."""
    assert "content" in response
    assert response["content"][0]["type"] == expected_type
    if expected_type == "text":
        assert "text" in response["content"][0]
    elif expected_type == "json":
        assert "data" in response["content"][0]
