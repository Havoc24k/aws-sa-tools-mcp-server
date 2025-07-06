"""
Test cases for aws_regions configuration module
"""

from aws_mcp_server.config.aws_regions import (
    AWS_REGIONS,
    get_all_regions,
    get_nearest_regions,
    get_region_info,
    get_regions_by_area,
    is_valid_region,
)


class TestAwsRegions:
    """Test AWS regions configuration"""

    def test_aws_regions_structure(self):
        """Test that AWS_REGIONS has correct structure"""
        assert isinstance(AWS_REGIONS, dict)
        assert "us" in AWS_REGIONS
        assert "eu" in AWS_REGIONS
        assert "ap" in AWS_REGIONS
        assert "other" in AWS_REGIONS

        # Test that each area contains regions
        for area, regions in AWS_REGIONS.items():
            assert isinstance(regions, dict)
            assert len(regions) > 0

            # Test that each region has required info
            for region_code, region_info in regions.items():
                assert isinstance(region_code, str)
                assert isinstance(region_info, dict)
                assert "name" in region_info
                assert "availability_zones" in region_info
                assert isinstance(region_info["name"], str)
                assert isinstance(region_info["availability_zones"], int)
                assert region_info["availability_zones"] > 0

    def test_get_all_regions(self):
        """Test get_all_regions function"""
        all_regions = get_all_regions()

        assert isinstance(all_regions, set)
        assert len(all_regions) > 0

        # Test that it includes known regions
        assert "us-east-1" in all_regions
        assert "eu-west-1" in all_regions
        assert "ap-southeast-1" in all_regions

        # Test that all regions from AWS_REGIONS are included
        expected_regions = set()
        for area_regions in AWS_REGIONS.values():
            expected_regions.update(area_regions.keys())

        assert all_regions == expected_regions

    def test_get_regions_by_area_valid_areas(self):
        """Test get_regions_by_area with valid areas"""
        # Test US regions
        us_regions = get_regions_by_area("us")
        assert isinstance(us_regions, list)
        assert "us-east-1" in us_regions
        assert "us-west-2" in us_regions
        assert len(us_regions) == len(AWS_REGIONS["us"])

        # Test EU regions
        eu_regions = get_regions_by_area("eu")
        assert isinstance(eu_regions, list)
        assert "eu-west-1" in eu_regions
        assert "eu-central-1" in eu_regions
        assert len(eu_regions) == len(AWS_REGIONS["eu"])

        # Test AP regions
        ap_regions = get_regions_by_area("ap")
        assert isinstance(ap_regions, list)
        assert "ap-southeast-1" in ap_regions
        assert "ap-northeast-1" in ap_regions
        assert len(ap_regions) == len(AWS_REGIONS["ap"])

        # Test other regions
        other_regions = get_regions_by_area("other")
        assert isinstance(other_regions, list)
        assert "sa-east-1" in other_regions
        assert "ca-central-1" in other_regions
        assert len(other_regions) == len(AWS_REGIONS["other"])

    def test_get_regions_by_area_invalid_area(self):
        """Test get_regions_by_area with invalid area"""
        invalid_regions = get_regions_by_area("invalid-area")
        assert isinstance(invalid_regions, list)
        assert len(invalid_regions) == 0

    def test_get_region_info_valid_regions(self):
        """Test get_region_info with valid regions"""
        # Test us-east-1
        us_east_info = get_region_info("us-east-1")
        assert isinstance(us_east_info, dict)
        assert us_east_info["name"] == "N. Virginia"
        assert us_east_info["availability_zones"] == 6

        # Test eu-west-1
        eu_west_info = get_region_info("eu-west-1")
        assert isinstance(eu_west_info, dict)
        assert eu_west_info["name"] == "Ireland"
        assert eu_west_info["availability_zones"] == 3

        # Test ap-southeast-1
        ap_southeast_info = get_region_info("ap-southeast-1")
        assert isinstance(ap_southeast_info, dict)
        assert ap_southeast_info["name"] == "Singapore"
        assert ap_southeast_info["availability_zones"] == 3

    def test_get_region_info_invalid_region(self):
        """Test get_region_info with invalid region"""
        invalid_info = get_region_info("invalid-region")
        assert isinstance(invalid_info, dict)
        assert len(invalid_info) == 0

    def test_is_valid_region_valid_regions(self):
        """Test is_valid_region with valid regions"""
        assert is_valid_region("us-east-1") is True
        assert is_valid_region("us-west-2") is True
        assert is_valid_region("eu-west-1") is True
        assert is_valid_region("ap-southeast-1") is True
        assert is_valid_region("sa-east-1") is True

    def test_is_valid_region_invalid_regions(self):
        """Test is_valid_region with invalid regions"""
        assert is_valid_region("invalid-region") is False
        assert is_valid_region("us-invalid-1") is False
        assert is_valid_region("") is False
        assert is_valid_region("us") is False

    def test_get_nearest_regions_valid_regions(self):
        """Test get_nearest_regions with valid regions"""
        # Test US region
        us_nearest = get_nearest_regions("us-east-1")
        assert isinstance(us_nearest, list)
        assert "us-east-1" not in us_nearest  # Should not include itself
        assert "us-east-2" in us_nearest
        assert "us-west-1" in us_nearest
        assert "us-west-2" in us_nearest
        assert len(us_nearest) == len(AWS_REGIONS["us"]) - 1

        # Test EU region
        eu_nearest = get_nearest_regions("eu-west-1")
        assert isinstance(eu_nearest, list)
        assert "eu-west-1" not in eu_nearest  # Should not include itself
        assert "eu-west-2" in eu_nearest
        assert "eu-central-1" in eu_nearest
        # Should not include regions from other areas
        assert "us-east-1" not in eu_nearest
        assert "ap-southeast-1" not in eu_nearest

        # Test AP region
        ap_nearest = get_nearest_regions("ap-southeast-1")
        assert isinstance(ap_nearest, list)
        assert "ap-southeast-1" not in ap_nearest  # Should not include itself
        assert "ap-southeast-2" in ap_nearest
        assert "ap-northeast-1" in ap_nearest
        # Should not include regions from other areas
        assert "us-east-1" not in ap_nearest
        assert "eu-west-1" not in ap_nearest

    def test_get_nearest_regions_invalid_region(self):
        """Test get_nearest_regions with invalid region"""
        invalid_nearest = get_nearest_regions("invalid-region")
        assert isinstance(invalid_nearest, list)
        assert len(invalid_nearest) == 0

    def test_region_consistency(self):
        """Test consistency between different functions"""
        all_regions = get_all_regions()

        # Test that every region in AWS_REGIONS is considered valid
        for area_regions in AWS_REGIONS.values():
            for region in area_regions.keys():
                assert is_valid_region(region)
                assert region in all_regions

                # Test that region info is accessible
                region_info = get_region_info(region)
                assert len(region_info) > 0
                assert "name" in region_info
                assert "availability_zones" in region_info

    def test_area_coverage(self):
        """Test that all areas are properly covered"""
        # Get all regions by iterating through areas
        regions_by_area = set()
        for area in ["us", "eu", "ap", "other"]:
            regions_by_area.update(get_regions_by_area(area))

        # Should equal all regions
        all_regions = get_all_regions()
        assert regions_by_area == all_regions

    def test_region_names_unique(self):
        """Test that region names are unique within each area"""
        for area, regions in AWS_REGIONS.items():
            region_names = [info["name"] for info in regions.values()]
            assert len(region_names) == len(set(region_names)), (
                f"Duplicate names in {area}"
            )

    def test_minimum_availability_zones(self):
        """Test that all regions have reasonable number of availability zones"""
        for area_regions in AWS_REGIONS.values():
            for region_info in area_regions.values():
                az_count = region_info["availability_zones"]
                assert az_count >= 2, "All regions should have at least 2 AZs"
                assert az_count <= 10, "No region should have more than 10 AZs"
