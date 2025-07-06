"""
Test cases for generic SDK wrapper service
"""

from unittest.mock import MagicMock, patch

import pytest

from aws_mcp_server.services.generic.sdk_wrapper import aws_sdk_wrapper, get_aws_config


class TestGetAwsConfig:
    """Test get_aws_config function"""

    def test_get_aws_config_success(self):
        """Test get_aws_config returns available profiles"""
        mock_profiles = ["default", "production", "development"]

        with patch(
            "aws_mcp_server.services.generic.sdk_wrapper.boto3.Session"
        ) as mock_session_class:
            mock_session = MagicMock()
            mock_session.available_profiles = mock_profiles
            mock_session_class.return_value = mock_session

            result = get_aws_config()

            assert result == mock_profiles
            mock_session_class.assert_called_once()

    def test_get_aws_config_empty_profiles(self):
        """Test get_aws_config with no profiles"""
        with patch(
            "aws_mcp_server.services.generic.sdk_wrapper.boto3.Session"
        ) as mock_session_class:
            mock_session = MagicMock()
            mock_session.available_profiles = []
            mock_session_class.return_value = mock_session

            result = get_aws_config()

            assert result == []
            mock_session_class.assert_called_once()

    def test_get_aws_config_boto3_exception(self):
        """Test get_aws_config when boto3 raises exception"""
        with patch(
            "aws_mcp_server.services.generic.sdk_wrapper.boto3.Session"
        ) as mock_session_class:
            mock_session_class.side_effect = Exception("AWS config error")

            with pytest.raises(Exception, match="AWS config error"):
                get_aws_config()


class TestAwsSdkWrapper:
    """Test aws_sdk_wrapper function"""

    @pytest.mark.asyncio
    async def test_aws_sdk_wrapper_success(self):
        """Test aws_sdk_wrapper with successful operation"""
        expected_response = {"Buckets": [{"Name": "test-bucket"}]}

        with patch(
            "aws_mcp_server.services.generic.sdk_wrapper.boto3.Session"
        ) as mock_session_class:
            mock_session = MagicMock()
            mock_client = MagicMock()
            mock_method = MagicMock(return_value=expected_response)

            mock_session_class.return_value = mock_session
            mock_session.client.return_value = mock_client
            mock_client.list_buckets = mock_method

            result = await aws_sdk_wrapper(
                service_name="s3",
                operation_name="list_buckets",
                region_name="us-east-1",
                profile_name="default",
                operation_kwargs={},
            )

            assert result == expected_response
            mock_session_class.assert_called_once_with(profile_name="default")
            mock_session.client.assert_called_once_with("s3", region_name="us-east-1")
            mock_method.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_aws_sdk_wrapper_with_kwargs(self):
        """Test aws_sdk_wrapper with operation kwargs"""
        expected_response = {"Reservations": []}
        operation_kwargs = {"InstanceIds": ["i-1234567890abcdef0"]}

        with patch(
            "aws_mcp_server.services.generic.sdk_wrapper.boto3.Session"
        ) as mock_session_class:
            mock_session = MagicMock()
            mock_client = MagicMock()
            mock_method = MagicMock(return_value=expected_response)

            mock_session_class.return_value = mock_session
            mock_session.client.return_value = mock_client
            mock_client.describe_instances = mock_method

            result = await aws_sdk_wrapper(
                service_name="ec2",
                operation_name="describe_instances",
                region_name="eu-west-1",
                profile_name="production",
                operation_kwargs=operation_kwargs,
            )

            assert result == expected_response
            mock_session_class.assert_called_once_with(profile_name="production")
            mock_session.client.assert_called_once_with("ec2", region_name="eu-west-1")
            mock_method.assert_called_once_with(**operation_kwargs)

    @pytest.mark.asyncio
    async def test_aws_sdk_wrapper_complex_kwargs(self):
        """Test aws_sdk_wrapper with complex operation kwargs"""
        expected_response = {"GroupDefinitions": [], "ResultsByTime": []}
        operation_kwargs = {
            "TimePeriod": {"Start": "2023-01-01", "End": "2023-01-31"},
            "Granularity": "MONTHLY",
            "Metrics": ["BlendedCost"],
            "GroupBy": [{"Type": "DIMENSION", "Key": "SERVICE"}],
        }

        with patch(
            "aws_mcp_server.services.generic.sdk_wrapper.boto3.Session"
        ) as mock_session_class:
            mock_session = MagicMock()
            mock_client = MagicMock()
            mock_method = MagicMock(return_value=expected_response)

            mock_session_class.return_value = mock_session
            mock_session.client.return_value = mock_client
            mock_client.get_cost_and_usage = mock_method

            result = await aws_sdk_wrapper(
                service_name="ce",
                operation_name="get_cost_and_usage",
                region_name="us-east-1",
                profile_name="default",
                operation_kwargs=operation_kwargs,
            )

            assert result == expected_response
            mock_method.assert_called_once_with(**operation_kwargs)

    @pytest.mark.asyncio
    async def test_aws_sdk_wrapper_session_creation_error(self):
        """Test aws_sdk_wrapper when session creation fails"""
        with patch(
            "aws_mcp_server.services.generic.sdk_wrapper.boto3.Session"
        ) as mock_session_class:
            mock_session_class.side_effect = Exception("Invalid profile")

            with pytest.raises(Exception, match="Invalid profile"):
                await aws_sdk_wrapper(
                    service_name="s3",
                    operation_name="list_buckets",
                    region_name="us-east-1",
                    profile_name="invalid",
                    operation_kwargs={},
                )

    @pytest.mark.asyncio
    async def test_aws_sdk_wrapper_client_creation_error(self):
        """Test aws_sdk_wrapper when client creation fails"""
        with patch(
            "aws_mcp_server.services.generic.sdk_wrapper.boto3.Session"
        ) as mock_session_class:
            mock_session = MagicMock()
            mock_session.client.side_effect = Exception("Invalid service")
            mock_session_class.return_value = mock_session

            with pytest.raises(Exception, match="Invalid service"):
                await aws_sdk_wrapper(
                    service_name="invalid_service",
                    operation_name="list_something",
                    region_name="us-east-1",
                    profile_name="default",
                    operation_kwargs={},
                )

    @pytest.mark.asyncio
    async def test_aws_sdk_wrapper_method_not_found(self):
        """Test aws_sdk_wrapper when operation method doesn't exist"""
        with patch(
            "aws_mcp_server.services.generic.sdk_wrapper.boto3.Session"
        ) as mock_session_class:
            mock_session = MagicMock()
            # Create a mock client with a limited spec so it doesn't have invalid_operation
            mock_client = MagicMock(spec=["list_buckets", "describe_instances"])
            mock_session_class.return_value = mock_session
            mock_session.client.return_value = mock_client

            with pytest.raises(AttributeError):
                await aws_sdk_wrapper(
                    service_name="s3",
                    operation_name="invalid_operation",
                    region_name="us-east-1",
                    profile_name="default",
                    operation_kwargs={},
                )

    @pytest.mark.asyncio
    async def test_aws_sdk_wrapper_operation_error(self):
        """Test aws_sdk_wrapper when operation execution fails"""
        with patch(
            "aws_mcp_server.services.generic.sdk_wrapper.boto3.Session"
        ) as mock_session_class:
            mock_session = MagicMock()
            mock_client = MagicMock()
            mock_method = MagicMock(side_effect=Exception("Operation failed"))

            mock_session_class.return_value = mock_session
            mock_session.client.return_value = mock_client
            mock_client.list_buckets = mock_method

            with pytest.raises(Exception, match="Operation failed"):
                await aws_sdk_wrapper(
                    service_name="s3",
                    operation_name="list_buckets",
                    region_name="us-east-1",
                    profile_name="default",
                    operation_kwargs={},
                )

    @pytest.mark.asyncio
    async def test_aws_sdk_wrapper_different_services(self):
        """Test aws_sdk_wrapper with different AWS services"""
        services_tests = [
            ("s3", "list_buckets"),
            ("ec2", "describe_instances"),
            ("rds", "describe_db_instances"),
            ("lambda", "list_functions"),
            ("iam", "list_users"),
        ]

        for service_name, operation_name in services_tests:
            expected_response = {"test": "response"}

            with patch(
                "aws_mcp_server.services.generic.sdk_wrapper.boto3.Session"
            ) as mock_session_class:
                mock_session = MagicMock()
                mock_client = MagicMock()
                mock_method = MagicMock(return_value=expected_response)

                mock_session_class.return_value = mock_session
                mock_session.client.return_value = mock_client
                setattr(mock_client, operation_name, mock_method)

                result = await aws_sdk_wrapper(
                    service_name=service_name,
                    operation_name=operation_name,
                    region_name="us-east-1",
                    profile_name="default",
                    operation_kwargs={},
                )

                assert result == expected_response
                mock_session.client.assert_called_once_with(
                    service_name, region_name="us-east-1"
                )

    @pytest.mark.asyncio
    async def test_aws_sdk_wrapper_different_regions(self):
        """Test aws_sdk_wrapper with different AWS regions"""
        regions = [
            "us-east-1",
            "us-west-2",
            "eu-west-1",
            "ap-southeast-1",
            "ca-central-1",
        ]

        for region in regions:
            expected_response = {"Region": region}

            with patch(
                "aws_mcp_server.services.generic.sdk_wrapper.boto3.Session"
            ) as mock_session_class:
                mock_session = MagicMock()
                mock_client = MagicMock()
                mock_method = MagicMock(return_value=expected_response)

                mock_session_class.return_value = mock_session
                mock_session.client.return_value = mock_client
                mock_client.list_buckets = mock_method

                result = await aws_sdk_wrapper(
                    service_name="s3",
                    operation_name="list_buckets",
                    region_name=region,
                    profile_name="default",
                    operation_kwargs={},
                )

                assert result == expected_response
                mock_session.client.assert_called_once_with("s3", region_name=region)

    @pytest.mark.asyncio
    async def test_aws_sdk_wrapper_different_profiles(self):
        """Test aws_sdk_wrapper with different AWS profiles"""
        profiles = ["default", "production", "development", "staging"]

        for profile in profiles:
            expected_response = {"Profile": profile}

            with patch(
                "aws_mcp_server.services.generic.sdk_wrapper.boto3.Session"
            ) as mock_session_class:
                mock_session = MagicMock()
                mock_client = MagicMock()
                mock_method = MagicMock(return_value=expected_response)

                mock_session_class.return_value = mock_session
                mock_session.client.return_value = mock_client
                mock_client.list_buckets = mock_method

                result = await aws_sdk_wrapper(
                    service_name="s3",
                    operation_name="list_buckets",
                    region_name="us-east-1",
                    profile_name=profile,
                    operation_kwargs={},
                )

                assert result == expected_response
                mock_session_class.assert_called_with(profile_name=profile)
