"""Simple integration tests for S3 service tools."""

import boto3
import pytest
from moto import mock_aws


class TestS3ServiceSimple:
    """Test S3 service integration with simple setup."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.aws
    async def test_list_buckets_basic(self):
        """Test S3 list buckets basic functionality."""
        with mock_aws():
            # Create test buckets
            s3_client = boto3.client("s3", region_name="us-east-1")
            test_buckets = ["test-bucket-1", "test-bucket-2"]

            for bucket in test_buckets:
                s3_client.create_bucket(Bucket=bucket)

            # Test the function
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
    async def test_list_objects_v2_basic(self):
        """Test S3 list objects v2 basic functionality."""
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

            # Test the function
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


class TestS3ServiceErrors:
    """Test S3 service error handling."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.aws
    async def test_list_objects_v2_nonexistent_bucket(self):
        """Test S3 list objects v2 with nonexistent bucket."""
        with mock_aws():
            from aws_mcp_server.services.storage.s3 import s3_list_objects_v2

            # This should raise an exception for nonexistent bucket
            with pytest.raises((Exception, ValueError, KeyError)):
                await s3_list_objects_v2(
                    profile_name="test",
                    region="us-east-1",
                    bucket_name="nonexistent-bucket-12345",
                )
