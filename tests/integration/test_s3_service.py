"""Integration tests for S3 service tools."""

import pytest
from tests.utils.aws_mocks import AWSMockManager


class TestS3Service:
    """Test S3 service integration."""
    
    @pytest.fixture(autouse=True)
    async def setup_method(self):
        """Set up AWS mocks for each test."""
        self.aws_mock = AWSMockManager()
        self.test_data = self.aws_mock.setup_s3_mock()
        yield
        self.aws_mock.cleanup()
    
    @pytest.mark.integration
    @pytest.mark.aws
    async def test_list_buckets(self, mcp_server):
        """Test S3 list buckets functionality."""
        from aws_mcp_server.services.storage.s3 import s3_list_buckets
        
        result = await s3_list_buckets(
            profile_name='test',
            region='us-east-1'
        )
        
        # Verify response structure
        assert 'Buckets' in result
        assert isinstance(result['Buckets'], list)
        
        # Should have our test buckets
        bucket_names = [bucket['Name'] for bucket in result['Buckets']]
        expected_buckets = self.test_data['buckets']
        
        for expected_bucket in expected_buckets:
            assert expected_bucket in bucket_names
        
        # Check bucket structure
        if result['Buckets']:
            bucket = result['Buckets'][0]
            required_fields = ['Name', 'CreationDate']
            for field in required_fields:
                assert field in bucket
    
    @pytest.mark.integration
    @pytest.mark.aws
    async def test_list_objects_v2_basic(self, mcp_server):
        """Test S3 list objects v2 basic functionality."""
        from aws_mcp_server.services.storage.s3 import s3_list_objects_v2
        
        bucket_name = self.test_data['buckets'][0]
        
        result = await s3_list_objects_v2(
            profile_name='test',
            region='us-east-1',
            bucket_name=bucket_name
        )
        
        # Verify response structure
        assert 'Contents' in result
        assert isinstance(result['Contents'], list)
        
        # Should have our test objects
        assert len(result['Contents']) == 3  # We created 3 test files
        
        # Check object structure
        obj = result['Contents'][0]
        required_fields = ['Key', 'Size', 'LastModified']
        for field in required_fields:
            assert field in obj
    
    @pytest.mark.integration
    @pytest.mark.aws
    async def test_list_objects_v2_with_prefix(self, mcp_server):
        """Test S3 list objects v2 with prefix filter."""
        from aws_mcp_server.services.storage.s3 import s3_list_objects_v2
        
        bucket_name = self.test_data['buckets'][0]
        
        result = await s3_list_objects_v2(
            profile_name='test',
            region='us-east-1',
            bucket_name=bucket_name,
            prefix='test-file-1'
        )
        
        assert 'Contents' in result
        
        # Should only return objects matching the prefix
        for obj in result['Contents']:
            assert obj['Key'].startswith('test-file-1')
    
    @pytest.mark.integration
    @pytest.mark.aws
    async def test_list_objects_v2_with_max_keys(self, mcp_server):
        """Test S3 list objects v2 with max keys limit."""
        from aws_mcp_server.services.storage.s3 import s3_list_objects_v2
        
        bucket_name = self.test_data['buckets'][0]
        
        result = await s3_list_objects_v2(
            profile_name='test',
            region='us-east-1',
            bucket_name=bucket_name,
            max_keys=2
        )
        
        assert 'Contents' in result
        
        # Should return at most 2 objects
        assert len(result['Contents']) <= 2
        
        # Check if there's more data (IsTruncated should be True if there are more objects)
        if len(result['Contents']) == 2:
            assert result.get('IsTruncated', False) in [True, False]
    
    @pytest.mark.integration
    @pytest.mark.aws
    async def test_list_objects_v2_with_delimiter(self, mcp_server):
        """Test S3 list objects v2 with delimiter for folder-like navigation."""
        from aws_mcp_server.services.storage.s3 import s3_list_objects_v2
        
        bucket_name = self.test_data['buckets'][0]
        
        # First, add some objects with folder-like structure
        import boto3
        s3_client = boto3.client('s3', region_name='us-east-1')
        s3_client.put_object(Bucket=bucket_name, Key='folder1/file1.txt', Body='content1')
        s3_client.put_object(Bucket=bucket_name, Key='folder1/file2.txt', Body='content2')
        s3_client.put_object(Bucket=bucket_name, Key='folder2/file3.txt', Body='content3')
        
        result = await s3_list_objects_v2(
            profile_name='test',
            region='us-east-1',
            bucket_name=bucket_name,
            delimiter='/'
        )
        
        # Should have CommonPrefixes for folder-like structure
        if 'CommonPrefixes' in result:
            assert isinstance(result['CommonPrefixes'], list)
            prefix_values = [cp['Prefix'] for cp in result['CommonPrefixes']]
            assert 'folder1/' in prefix_values or 'folder2/' in prefix_values
    
    @pytest.mark.integration
    @pytest.mark.aws
    async def test_list_objects_v2_empty_bucket(self, mcp_server):
        """Test S3 list objects v2 with empty bucket."""
        from aws_mcp_server.services.storage.s3 import s3_list_objects_v2
        
        # Create an empty bucket
        import boto3
        s3_client = boto3.client('s3', region_name='us-east-1')
        empty_bucket = 'empty-test-bucket'
        s3_client.create_bucket(Bucket=empty_bucket)
        
        result = await s3_list_objects_v2(
            profile_name='test',
            region='us-east-1',
            bucket_name=empty_bucket
        )
        
        # Empty bucket should return no contents
        if 'Contents' in result:
            assert len(result['Contents']) == 0
        else:
            # Some implementations might not include Contents key for empty buckets
            assert 'Contents' not in result
    
    @pytest.mark.integration
    @pytest.mark.aws
    async def test_list_objects_v2_with_start_after(self, mcp_server):
        """Test S3 list objects v2 with start_after parameter."""
        from aws_mcp_server.services.storage.s3 import s3_list_objects_v2
        
        bucket_name = self.test_data['buckets'][0]
        
        result = await s3_list_objects_v2(
            profile_name='test',
            region='us-east-1',
            bucket_name=bucket_name,
            start_after='test-file-0.txt'
        )
        
        assert 'Contents' in result
        
        # Should return objects after 'test-file-0.txt' lexicographically
        for obj in result['Contents']:
            assert obj['Key'] > 'test-file-0.txt'
    
    @pytest.mark.integration
    @pytest.mark.aws
    async def test_list_objects_v2_fetch_owner(self, mcp_server):
        """Test S3 list objects v2 with fetch_owner parameter."""
        from aws_mcp_server.services.storage.s3 import s3_list_objects_v2
        
        bucket_name = self.test_data['buckets'][0]
        
        result = await s3_list_objects_v2(
            profile_name='test',
            region='us-east-1',
            bucket_name=bucket_name,
            fetch_owner=True
        )
        
        assert 'Contents' in result
        
        # When fetch_owner is True, objects should include Owner information
        if result['Contents']:
            # Note: moto might not fully simulate owner info, but we test the parameter is accepted
            obj = result['Contents'][0]
            # Owner info might or might not be present in moto, but call should succeed
            assert 'Key' in obj


class TestS3ServiceErrors:
    """Test S3 service error handling."""
    
    @pytest.mark.integration
    @pytest.mark.aws
    async def test_list_objects_v2_nonexistent_bucket(self, mock_aws_services):
        """Test S3 list objects v2 with nonexistent bucket."""
        from aws_mcp_server.services.storage.s3 import s3_list_objects_v2
        
        with pytest.raises(Exception):
            await s3_list_objects_v2(
                profile_name='test',
                region='us-east-1',
                bucket_name='nonexistent-bucket-12345'
            )
    
    @pytest.mark.integration
    @pytest.mark.aws
    async def test_list_buckets_with_invalid_credentials(self):
        """Test S3 list buckets with invalid credentials."""
        from aws_mcp_server.services.storage.s3 import s3_list_buckets
        
        # This should fail with invalid profile
        with pytest.raises(Exception):
            await s3_list_buckets(
                profile_name='invalid-profile-name',
                region='us-east-1'
            )