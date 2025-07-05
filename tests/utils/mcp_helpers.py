"""MCP testing helpers and utilities."""

import json
from typing import Any, Optional

from fastmcp import FastMCP


class MCPTestHelper:
    """Helper class for testing MCP functionality."""

    @staticmethod
    def validate_tool_response(
        response: dict[str, Any], expected_content_type: str = "text"
    ) -> bool:
        """Validate MCP tool response format.

        Args:
            response: MCP tool response
            expected_content_type: Expected content type ('text' or 'json')

        Returns:
            True if valid format
        """
        try:
            assert "content" in response
            assert isinstance(response["content"], list)
            assert len(response["content"]) > 0

            content_item = response["content"][0]
            assert "type" in content_item
            assert content_item["type"] == expected_content_type

            if expected_content_type == "text":
                assert "text" in content_item
                assert isinstance(content_item["text"], str)
            elif expected_content_type == "json":
                assert "data" in content_item

            return True
        except (AssertionError, KeyError, IndexError):
            return False

    @staticmethod
    def create_mock_tool_args(tool_name: str, **kwargs) -> dict[str, Any]:
        """Create mock arguments for MCP tool calls.

        Args:
            tool_name: Name of the tool
            **kwargs: Tool arguments

        Returns:
            Dictionary of tool arguments
        """
        base_args = {"profile_name": "test", "region": "us-east-1"}
        base_args.update(kwargs)
        return base_args

    @staticmethod
    def extract_tool_result_data(response: dict[str, Any]) -> Any:
        """Extract data from MCP tool response.

        Args:
            response: MCP tool response

        Returns:
            Extracted data
        """
        if "content" in response and response["content"]:
            content = response["content"][0]
            if content.get("type") == "text":
                return content.get("text")
            elif content.get("type") == "json":
                return content.get("data")
        return None

    @staticmethod
    def validate_aws_response_structure(data: Any, service: str) -> bool:
        """Validate AWS response structure.

        Args:
            data: Response data to validate
            service: AWS service name

        Returns:
            True if valid structure
        """
        if not isinstance(data, dict):
            return False

        # Check for AWS response metadata
        if "ResponseMetadata" in data:
            metadata = data["ResponseMetadata"]
            if not all(key in metadata for key in ["RequestId", "HTTPStatusCode"]):
                return False

        # Service-specific validations
        service_validators = {
            "ec2": lambda d: "Reservations" in d
            or "SecurityGroups" in d
            or "Vpcs" in d,
            "s3": lambda d: "Buckets" in d or "Contents" in d or "Name" in d,
            "rds": lambda d: "DBInstances" in d,
            "cloudwatch": lambda d: "Datapoints" in d or "MetricDataResults" in d,
            "ce": lambda d: "ResultsByTime" in d or "GroupDefinitions" in d,
        }

        validator = service_validators.get(service)
        if validator:
            return validator(data)

        return True  # Unknown service, assume valid

    @staticmethod
    async def test_tool_with_args(
        client, tool_name: str, args: dict[str, Any]
    ) -> dict[str, Any]:
        """Test MCP tool with given arguments.

        Args:
            client: FastMCP client
            tool_name: Name of the tool to test
            args: Tool arguments

        Returns:
            Tool response
        """
        try:
            response = await client.call_tool(tool_name, args)
            return {"success": True, "response": response, "error": None}
        except Exception as e:
            return {"success": False, "response": None, "error": str(e)}

    @staticmethod
    def create_test_scenarios() -> dict[str, dict[str, Any]]:
        """Create common test scenarios for AWS tools.

        Returns:
            Dictionary of test scenarios
        """
        return {
            "ec2_basic": {
                "tool": "ec2-describe_instances",
                "args": {"profile_name": "test", "region": "us-east-1"},
                "expected_keys": ["Reservations"],
            },
            "ec2_with_filters": {
                "tool": "ec2-describe_instances",
                "args": {
                    "profile_name": "test",
                    "region": "us-east-1",
                    "filters": {"instance-state-name": ["running"]},
                },
                "expected_keys": ["Reservations"],
            },
            "s3_list_buckets": {
                "tool": "s3-list_buckets",
                "args": {"profile_name": "test", "region": "us-east-1"},
                "expected_keys": ["Buckets"],
            },
            "s3_list_objects": {
                "tool": "s3-list_objects_v2",
                "args": {
                    "profile_name": "test",
                    "region": "us-east-1",
                    "bucket_name": "test-bucket",
                },
                "expected_keys": ["Contents"],
            },
            "rds_basic": {
                "tool": "rds-describe_db_instances",
                "args": {"profile_name": "test", "region": "us-east-1"},
                "expected_keys": ["DBInstances"],
            },
        }


class MCPServerTestSuite:
    """Test suite for comprehensive MCP server testing."""

    def __init__(self, server: FastMCP):
        self.server = server
        self.helper = MCPTestHelper()

    async def test_all_tools(self, client) -> dict[str, Any]:
        """Test all available tools.

        Args:
            client: FastMCP client

        Returns:
            Test results summary
        """
        results = {
            "total_tools": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "errors": [],
        }

        # Get all available tools
        tools_response = await client.list_tools()
        tools = tools_response.get("tools", [])
        results["total_tools"] = len(tools)

        # Test each tool with basic parameters
        for tool in tools:
            tool_name = tool["name"]
            try:
                args = self.helper.create_mock_tool_args(tool_name)
                response = await client.call_tool(tool_name, args)

                if self.helper.validate_tool_response(response):
                    results["successful_tests"] += 1
                else:
                    results["failed_tests"] += 1
                    results["errors"].append(f"Invalid response format for {tool_name}")

            except Exception as e:
                results["failed_tests"] += 1
                results["errors"].append(f"Error testing {tool_name}: {str(e)}")

        return results

    async def test_resources(self, client) -> dict[str, Any]:
        """Test all available resources.

        Args:
            client: FastMCP client

        Returns:
            Resource test results
        """
        results = {
            "total_resources": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "errors": [],
        }

        try:
            resources_response = await client.list_resources()
            resources = resources_response.get("resources", [])
            results["total_resources"] = len(resources)

            for resource in resources:
                try:
                    resource_response = await client.read_resource(resource["uri"])
                    if "contents" in resource_response:
                        results["successful_tests"] += 1
                    else:
                        results["failed_tests"] += 1
                        results["errors"].append(
                            f"Invalid resource response for {resource['uri']}"
                        )
                except Exception as e:
                    results["failed_tests"] += 1
                    results["errors"].append(
                        f"Error reading resource {resource['uri']}: {str(e)}"
                    )

        except Exception as e:
            results["errors"].append(f"Error listing resources: {str(e)}")

        return results
