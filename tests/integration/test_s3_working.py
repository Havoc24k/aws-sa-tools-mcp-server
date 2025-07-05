"""Working integration tests for S3 service tools."""

import pytest
import boto3
from moto import mock_aws
from unittest.mock import patch


class TestS3ServiceWorking:
    """Test S3 service integration with proper mocking."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.aws
    async def test_list_buckets_with_patched_session(self):
        """Test S3 list buckets with patched boto3 session."""
        with mock_aws():
            # Create test buckets
            s3_client = boto3.client("s3", region_name="us-east-1")
            test_buckets = ["test-bucket-1", "test-bucket-2"]

            for bucket in test_buckets:
                s3_client.create_bucket(Bucket=bucket)

            # Test the function by patching the session creation
            with patch("boto3.Session") as mock_session:
                mock_session.return_value = boto3.Session()
                mock_session.return_value.client = lambda *args, **kwargs: s3_client

                from aws_mcp_server.services.storage.s3 import s3_list_buckets

                result = await s3_list_buckets(profile_name="test", region="us-east-1")

                # Verify response structure
                assert "Buckets" in result
                assert isinstance(result["Buckets"], list)

                # Should have our test buckets
                bucket_names = [bucket["Name"] for bucket in result["Buckets"]]
                for expected_bucket in test_buckets:
                    assert expected_bucket in bucket_names

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.aws
    async def test_list_objects_v2_with_patched_session(self):
        """Test S3 list objects v2 with patched boto3 session."""
        with mock_aws():
            # Create test bucket and objects
            s3_client = boto3.client("s3", region_name="us-east-1")
            bucket_name = "test-bucket"
            s3_client.create_bucket(Bucket=bucket_name)

            # Add test objects
            test_objects = ["file1.txt", "file2.txt", "file3.txt"]
            for obj_key in test_objects:
                s3_client.put_object(
                    Bucket=bucket_name, Key=obj_key, Body=f"Content of {obj_key}"
                )

            # Test the function by patching the session creation
            with patch("boto3.Session") as mock_session:
                mock_session.return_value = boto3.Session()
                mock_session.return_value.client = lambda *args, **kwargs: s3_client

                from aws_mcp_server.services.storage.s3 import s3_list_objects_v2

                result = await s3_list_objects_v2(
                    profile_name="test", region="us-east-1", bucket_name=bucket_name
                )

                # Verify response structure
                assert "Contents" in result
                assert isinstance(result["Contents"], list)
                assert len(result["Contents"]) == len(test_objects)

                # Check object structure
                obj = result["Contents"][0]
                required_fields = ["Key", "Size", "LastModified"]
                for field in required_fields:
                    assert field in obj

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.aws
    async def test_s3_list_objects_v2_with_pagination(self):
        """Test S3 list objects v2 pagination parameters."""
        with mock_aws():
            # Create test bucket and objects
            s3_client = boto3.client("s3", region_name="us-east-1")
            bucket_name = "test-bucket"
            s3_client.create_bucket(Bucket=bucket_name)

            # Add test objects
            for i in range(5):
                s3_client.put_object(
                    Bucket=bucket_name, Key=f"file{i}.txt", Body=f"Content {i}"
                )

            # Test the function by patching the session creation
            with patch("boto3.Session") as mock_session:
                mock_session.return_value = boto3.Session()
                mock_session.return_value.client = lambda *args, **kwargs: s3_client

                from aws_mcp_server.services.storage.s3 import s3_list_objects_v2

                # Test with max_keys parameter
                result = await s3_list_objects_v2(
                    profile_name="test",
                    region="us-east-1",
                    bucket_name=bucket_name,
                    max_keys=3,
                )

                # Verify response structure
                assert "Contents" in result
                assert isinstance(result["Contents"], list)
                assert len(result["Contents"]) <= 3

                # Test with prefix parameter
                result = await s3_list_objects_v2(
                    profile_name="test",
                    region="us-east-1",
                    bucket_name=bucket_name,
                    prefix="file1",
                )

                # Should only return files starting with 'file1'
                assert "Contents" in result
                for obj in result["Contents"]:
                    assert obj["Key"].startswith("file1")
