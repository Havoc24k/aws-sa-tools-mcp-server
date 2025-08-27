"""
Test cases for aws_regions configuration module
"""

from unittest.mock import patch

from aws_mcp_server.config.aws_regions import (
    get_all_regions,
    get_regions_by_prefix,
    is_valid_region,
)


class TestAwsRegions:
    """Test AWS regions configuration using boto3 dynamic discovery"""

    def test_get_all_regions(self):
        """Test get_all_regions function"""
        all_regions = get_all_regions()

        assert isinstance(all_regions, set)
        assert len(all_regions) > 0

        # Test that it includes known regions (should be available in any AWS account)
        assert "us-east-1" in all_regions
        assert "us-west-2" in all_regions

    def test_get_all_regions_fallback(self):
        """Test get_all_regions fallback when boto3 fails"""
        with patch("boto3.Session") as mock_session:
            # Make boto3.Session().get_available_regions() raise an exception
            mock_session.return_value.get_available_regions.side_effect = Exception(
                "Mock error"
            )

            # Clear the cache to force re-execution
            get_all_regions.cache_clear()

            all_regions = get_all_regions()

            assert isinstance(all_regions, set)
            assert len(all_regions) > 0
            # Should include fallback regions
            assert "us-east-1" in all_regions
            assert "eu-west-1" in all_regions

    def test_get_regions_by_prefix(self):
        """Test get_regions_by_prefix function"""
        # Test US regions
        us_regions = get_regions_by_prefix("us")
        assert isinstance(us_regions, list)
        assert len(us_regions) > 0
        assert all(r.startswith("us") for r in us_regions)
        assert "us-east-1" in us_regions

        # Test EU regions
        eu_regions = get_regions_by_prefix("eu")
        assert isinstance(eu_regions, list)
        assert len(eu_regions) > 0
        assert all(r.startswith("eu") for r in eu_regions)

        # Test empty prefix should return all regions
        all_regions = get_regions_by_prefix("")
        assert len(all_regions) > 0

    def test_is_valid_region_valid_regions(self):
        """Test is_valid_region with known valid regions"""
        assert is_valid_region("us-east-1") is True
        assert is_valid_region("us-west-2") is True

    def test_is_valid_region_invalid_regions(self):
        """Test is_valid_region with invalid regions"""
        assert is_valid_region("invalid-region") is False
        assert is_valid_region("us-invalid-1") is False
        assert is_valid_region("") is False
        assert is_valid_region("us") is False

    def test_region_functions_consistency(self):
        """Test that functions work consistently together"""
        all_regions = get_all_regions()

        # Test that common regions are valid
        common_regions = ["us-east-1", "us-west-2"]
        for region in common_regions:
            if region in all_regions:  # Only test if the region is actually available
                assert is_valid_region(region)
