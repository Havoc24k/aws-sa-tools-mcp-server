"""Integration tests for EC2 service tools."""

import pytest

from tests.utils.aws_mocks import AWSMockManager


class TestEC2Service:
    """Test EC2 service integration."""

    @pytest.fixture(autouse=True)
    async def setup_method(self):
        """Set up AWS mocks for each test."""
        self.aws_mock = AWSMockManager()
        self.test_data = self.aws_mock.setup_ec2_mock()
        yield
        self.aws_mock.cleanup()

    @pytest.mark.integration
    @pytest.mark.aws
    async def test_describe_instances_basic(self, mcp_server):
        """Test basic EC2 describe instances functionality."""
        from aws_mcp_server.services.compute.ec2 import ec2_describe_instances

        result = await ec2_describe_instances(profile_name="test", region="us-east-1")

        # Verify response structure
        assert "Reservations" in result
        assert isinstance(result["Reservations"], list)

        # Should have created instances in setup
        assert len(result["Reservations"]) > 0

        # Check instance structure
        if result["Reservations"]:
            reservation = result["Reservations"][0]
            assert "Instances" in reservation
            instance = reservation["Instances"][0]

            # Verify instance has required fields
            required_fields = ["InstanceId", "State", "InstanceType"]
            for field in required_fields:
                assert field in instance

    @pytest.mark.integration
    @pytest.mark.aws
    async def test_describe_instances_with_filters(self, mcp_server):
        """Test EC2 describe instances with filters."""
        from aws_mcp_server.services.compute.ec2 import ec2_describe_instances

        # Test with instance state filter
        result = await ec2_describe_instances(
            profile_name="test",
            region="us-east-1",
            filters={"instance-state-name": ["running"]},
        )

        assert "Reservations" in result

        # All returned instances should be running
        for reservation in result["Reservations"]:
            for instance in reservation["Instances"]:
                assert instance["State"]["Name"] == "running"

    @pytest.mark.integration
    @pytest.mark.aws
    async def test_describe_instances_with_specific_ids(self, mcp_server):
        """Test EC2 describe instances with specific instance IDs."""
        from aws_mcp_server.services.compute.ec2 import ec2_describe_instances

        # Get instance IDs from test data
        instance_ids = self.test_data["instance_ids"]

        result = await ec2_describe_instances(
            profile_name="test",
            region="us-east-1",
            instance_ids=instance_ids[:1],  # Test with one instance
        )

        assert "Reservations" in result

        # Should return only the requested instance
        found_instance_ids = []
        for reservation in result["Reservations"]:
            for instance in reservation["Instances"]:
                found_instance_ids.append(instance["InstanceId"])

        assert len(found_instance_ids) == 1
        assert found_instance_ids[0] in instance_ids

    @pytest.mark.integration
    @pytest.mark.aws
    async def test_describe_security_groups(self, mcp_server):
        """Test EC2 describe security groups."""
        from aws_mcp_server.services.compute.ec2 import ec2_describe_security_groups

        result = await ec2_describe_security_groups(
            profile_name="test", region="us-east-1"
        )

        assert "SecurityGroups" in result
        assert isinstance(result["SecurityGroups"], list)

        # Should have at least the default security group
        assert len(result["SecurityGroups"]) >= 1

        # Check security group structure
        sg = result["SecurityGroups"][0]
        required_fields = ["GroupId", "GroupName", "Description"]
        for field in required_fields:
            assert field in sg

    @pytest.mark.integration
    @pytest.mark.aws
    async def test_describe_security_groups_with_filters(self, mcp_server):
        """Test EC2 describe security groups with VPC filter."""
        from aws_mcp_server.services.compute.ec2 import ec2_describe_security_groups

        vpc_id = self.test_data["vpc_id"]

        result = await ec2_describe_security_groups(
            profile_name="test", region="us-east-1", filters={"vpc-id": [vpc_id]}
        )

        assert "SecurityGroups" in result

        # All returned security groups should be in the specified VPC
        for sg in result["SecurityGroups"]:
            assert sg["VpcId"] == vpc_id

    @pytest.mark.integration
    @pytest.mark.aws
    async def test_describe_vpcs(self, mcp_server):
        """Test EC2 describe VPCs."""
        from aws_mcp_server.services.compute.ec2 import ec2_describe_vpcs

        result = await ec2_describe_vpcs(profile_name="test", region="us-east-1")

        assert "Vpcs" in result
        assert isinstance(result["Vpcs"], list)

        # Should have at least our test VPC
        assert len(result["Vpcs"]) >= 1

        # Check VPC structure
        vpc = result["Vpcs"][0]
        required_fields = ["VpcId", "State", "CidrBlock"]
        for field in required_fields:
            assert field in vpc

    @pytest.mark.integration
    @pytest.mark.aws
    async def test_describe_vpcs_with_specific_id(self, mcp_server):
        """Test EC2 describe VPCs with specific VPC ID."""
        from aws_mcp_server.services.compute.ec2 import ec2_describe_vpcs

        vpc_id = self.test_data["vpc_id"]

        result = await ec2_describe_vpcs(
            profile_name="test", region="us-east-1", vpc_ids=[vpc_id]
        )

        assert "Vpcs" in result
        assert len(result["Vpcs"]) == 1
        assert result["Vpcs"][0]["VpcId"] == vpc_id

    @pytest.mark.integration
    @pytest.mark.aws
    async def test_describe_instances_pagination(self, mcp_server):
        """Test EC2 describe instances with pagination."""
        from aws_mcp_server.services.compute.ec2 import ec2_describe_instances

        result = await ec2_describe_instances(
            profile_name="test", region="us-east-1", max_results=1
        )

        assert "Reservations" in result

        # With max_results=1, we should get at most 1 reservation
        assert len(result["Reservations"]) <= 1

    @pytest.mark.integration
    @pytest.mark.aws
    async def test_describe_instances_with_tag_filter(self, mcp_server):
        """Test EC2 describe instances with tag filter."""
        from aws_mcp_server.services.compute.ec2 import ec2_describe_instances

        result = await ec2_describe_instances(
            profile_name="test",
            region="us-east-1",
            filters={"tag:Environment": ["testing"]},
        )

        assert "Reservations" in result

        # Verify returned instances have the correct tag
        for reservation in result["Reservations"]:
            for instance in reservation["Instances"]:
                if "Tags" in instance:
                    environment_tags = [
                        tag["Value"]
                        for tag in instance["Tags"]
                        if tag["Key"] == "Environment"
                    ]
                    assert "testing" in environment_tags


class TestEC2ServiceErrors:
    """Test EC2 service error handling."""

    @pytest.mark.integration
    @pytest.mark.aws
    async def test_describe_instances_invalid_region(self):
        """Test EC2 describe instances with invalid region."""
        from aws_mcp_server.services.compute.ec2 import ec2_describe_instances

        with pytest.raises((Exception, ValueError, KeyError)):
            await ec2_describe_instances(
                profile_name="test", region="invalid-region-123"
            )

    @pytest.mark.integration
    @pytest.mark.aws
    async def test_describe_instances_nonexistent_instance_id(self, mock_aws_services):
        """Test EC2 describe instances with nonexistent instance ID."""
        from aws_mcp_server.services.compute.ec2 import ec2_describe_instances

        result = await ec2_describe_instances(
            profile_name="test", region="us-east-1", instance_ids=["i-nonexistent123"]
        )

        # Should return empty reservations for nonexistent instances
        assert "Reservations" in result
        assert len(result["Reservations"]) == 0
