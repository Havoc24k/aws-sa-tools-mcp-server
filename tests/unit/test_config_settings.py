"""
Test cases for settings configuration module
"""

import os
from unittest.mock import patch

import pytest

from aws_mcp_server.config import settings


class TestSettings:
    """Test simple settings configuration"""

    def test_settings_defaults(self):
        """Test settings with default values"""
        with patch.dict(os.environ, {}, clear=True):
            # Reimport to get fresh values
            import importlib

            from aws_mcp_server.config import settings as settings_module

            importlib.reload(settings_module)

            assert settings_module.DEFAULT_PORT == 8888
            assert settings_module.DEFAULT_TRANSPORT == "stdio"
            assert settings_module.DEBUG is False
            assert settings_module.DEFAULT_REGION == "us-east-1"
            assert settings_module.DEFAULT_PROFILE == "default"
            assert settings_module.MAX_CONCURRENT_REQUESTS == 10
            assert settings_module.ENABLE_PAGINATION is True

    def test_settings_from_environment_variables(self):
        """Test settings initialization from environment variables"""
        env_vars = {
            "AWS_MCP_PORT": "9999",
            "AWS_MCP_TRANSPORT": "sse",
            "AWS_MCP_DEBUG": "true",
            "AWS_DEFAULT_REGION": "eu-west-1",
            "AWS_PROFILE": "production",
            "AWS_MCP_MAX_CONCURRENT": "20",
            "AWS_MCP_ENABLE_PAGINATION": "false",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Reimport to get fresh values
            import importlib

            from aws_mcp_server.config import settings as settings_module

            importlib.reload(settings_module)

            assert settings_module.DEFAULT_PORT == 9999
            assert settings_module.DEFAULT_TRANSPORT == "sse"
            assert settings_module.DEBUG is True
            assert settings_module.DEFAULT_REGION == "eu-west-1"
            assert settings_module.DEFAULT_PROFILE == "production"
            assert settings_module.MAX_CONCURRENT_REQUESTS == 20
            assert settings_module.ENABLE_PAGINATION is False

    def test_settings_debug_variations(self):
        """Test debug setting with various string values"""
        # Test true values (only "true" case-insensitive)
        true_values = ["true", "True", "TRUE", "TrUe"]
        for value in true_values:
            with patch.dict(os.environ, {"AWS_MCP_DEBUG": value}, clear=True):
                import importlib

                from aws_mcp_server.config import settings as settings_module

                importlib.reload(settings_module)
                assert settings_module.DEBUG is True, f"Failed for value: {value}"

        # Test false values (anything that's not "true")
        false_values = [
            "false",
            "False",
            "FALSE",
            "0",
            "no",
            "No",
            "",
            "1",
            "yes",
            "Yes",
        ]
        for value in false_values:
            with patch.dict(os.environ, {"AWS_MCP_DEBUG": value}, clear=True):
                import importlib

                from aws_mcp_server.config import settings as settings_module

                importlib.reload(settings_module)
                assert settings_module.DEBUG is False, f"Failed for value: {value}"

    def test_settings_pagination_variations(self):
        """Test pagination setting with various string values"""
        # Test true values (only "true" case-insensitive)
        true_values = ["true", "True", "TRUE", "TrUe"]
        for value in true_values:
            with patch.dict(
                os.environ, {"AWS_MCP_ENABLE_PAGINATION": value}, clear=True
            ):
                import importlib

                from aws_mcp_server.config import settings as settings_module

                importlib.reload(settings_module)
                assert settings_module.ENABLE_PAGINATION is True, (
                    f"Failed for value: {value}"
                )

        # Test false values (anything that's not "true")
        false_values = [
            "false",
            "False",
            "FALSE",
            "0",
            "no",
            "No",
            "",
            "1",
            "yes",
            "Yes",
        ]
        for value in false_values:
            with patch.dict(
                os.environ, {"AWS_MCP_ENABLE_PAGINATION": value}, clear=True
            ):
                import importlib

                from aws_mcp_server.config import settings as settings_module

                importlib.reload(settings_module)
                assert settings_module.ENABLE_PAGINATION is False, (
                    f"Failed for value: {value}"
                )

    def test_settings_invalid_port(self):
        """Test settings with invalid port value"""
        with patch.dict(os.environ, {"AWS_MCP_PORT": "invalid"}, clear=True):
            with pytest.raises(ValueError):
                import importlib

                from aws_mcp_server.config import settings as settings_module

                importlib.reload(settings_module)

    def test_settings_invalid_max_concurrent(self):
        """Test settings with invalid max_concurrent value"""
        with patch.dict(os.environ, {"AWS_MCP_MAX_CONCURRENT": "invalid"}, clear=True):
            with pytest.raises(ValueError):
                import importlib

                from aws_mcp_server.config import settings as settings_module

                importlib.reload(settings_module)

    def test_service_specific_max_results(self):
        """Test service-specific max results configuration"""
        env_vars = {
            "AWS_MCP_MAX_RESULTS": "500",
            "AWS_MCP_EC2_INSTANCES_MAX": "1500",
            "AWS_MCP_RDS_INSTANCES_MAX": "50",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            import importlib

            from aws_mcp_server.config import settings as settings_module

            importlib.reload(settings_module)

            assert settings_module.DEFAULT_MAX_RESULTS == 500
            assert settings_module.EC2_INSTANCES_MAX == 1500
            assert settings_module.RDS_INSTANCES_MAX == 50
            # Should use default for others
            assert settings_module.EC2_SECURITY_GROUPS_MAX == 500

    def test_timeout_settings(self):
        """Test timeout configuration"""
        env_vars = {
            "AWS_MCP_TIMEOUT": "45",
            "AWS_MCP_API_TIMEOUT": "60",
            "AWS_MCP_PAGINATION_TIMEOUT": "600",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            import importlib

            from aws_mcp_server.config import settings as settings_module

            importlib.reload(settings_module)

            assert settings_module.DEFAULT_TIMEOUT == 45
            assert settings_module.AWS_API_CALL_TIMEOUT == 60
            assert settings_module.PAGINATION_TIMEOUT == 600

    def test_constants_structure(self):
        """Test that all required constants are defined"""
        required_constants = [
            "DEFAULT_PORT",
            "DEFAULT_TRANSPORT",
            "DEBUG",
            "DEFAULT_REGION",
            "DEFAULT_PROFILE",
            "MAX_CONCURRENT_REQUESTS",
            "ENABLE_PAGINATION",
            "DEFAULT_MAX_RESULTS",
            "DEFAULT_TIMEOUT",
            "EC2_INSTANCES_MAX",
            "EC2_SECURITY_GROUPS_MAX",
            "EC2_VPCS_MAX",
            "RDS_INSTANCES_MAX",
            "S3_OBJECTS_MAX",
            "AWS_API_CALL_TIMEOUT",
            "PAGINATION_TIMEOUT",
        ]

        for constant in required_constants:
            assert hasattr(settings, constant)
            value = getattr(settings, constant)
            assert value is not None

    def test_environment_case_sensitivity(self):
        """Test that environment variable names are case sensitive"""
        # Test with lowercase (should not work)
        with patch.dict(os.environ, {"aws_mcp_port": "9999"}, clear=True):
            import importlib

            from aws_mcp_server.config import settings as settings_module

            importlib.reload(settings_module)
            assert settings_module.DEFAULT_PORT == 8888  # Should use default

        # Test with correct case (should work)
        with patch.dict(os.environ, {"AWS_MCP_PORT": "9999"}, clear=True):
            import importlib

            from aws_mcp_server.config import settings as settings_module

            importlib.reload(settings_module)
            assert settings_module.DEFAULT_PORT == 9999

    def test_edge_cases(self):
        """Test settings with edge case values"""
        env_vars = {
            "AWS_MCP_PORT": "1",
            "AWS_MCP_MAX_CONCURRENT": "1",
            "AWS_MCP_MAX_RESULTS": "1",
            "AWS_MCP_TIMEOUT": "1",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            import importlib

            from aws_mcp_server.config import settings as settings_module

            importlib.reload(settings_module)

            assert settings_module.DEFAULT_PORT == 1
            assert settings_module.MAX_CONCURRENT_REQUESTS == 1
            assert settings_module.DEFAULT_MAX_RESULTS == 1
            assert settings_module.DEFAULT_TIMEOUT == 1
