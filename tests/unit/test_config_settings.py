"""Unit tests for modern configuration system."""

import os
from unittest.mock import patch

import pytest


class TestModernConfig:
    """Test modern dataclass-based configuration."""

    def test_config_defaults(self):
        """Test that default config values are correct."""
        with patch.dict(os.environ, {}, clear=True):
            from aws_mcp_server.core.config import AWSConfig, ServerConfig

            server_config = ServerConfig()
            aws_config = AWSConfig()

            # Test default values
            assert server_config.port == 8888
            assert server_config.transport == "stdio"
            assert server_config.debug is False
            assert aws_config.max_concurrent == 10
            assert aws_config.enable_pagination is True
            assert aws_config.max_results == 1000
            assert aws_config.timeout_seconds == 30

    def test_config_from_environment_variables(self):
        """Test that config can be overridden by environment variables."""
        env_vars = {
            "AWS_MCP_PORT": "9999",
            "AWS_MCP_TRANSPORT": "sse",
            "AWS_MCP_DEBUG": "true",
            "AWS_MCP_MAX_CONCURRENT": "20",
            "AWS_MCP_ENABLE_PAGINATION": "false",
            "AWS_MCP_MAX_RESULTS": "2000",
            "AWS_MCP_TIMEOUT": "60",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            from aws_mcp_server.core.config import AWSConfig, ServerConfig

            server_config = ServerConfig()
            aws_config = AWSConfig()

            assert server_config.port == 9999
            assert server_config.transport == "sse"
            assert server_config.debug is True
            assert aws_config.max_concurrent == 20
            assert aws_config.enable_pagination is False
            assert aws_config.max_results == 2000
            assert aws_config.timeout_seconds == 60

    def test_config_debug_variations(self):
        """Test different debug value variations."""
        debug_values = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("", False),
            ("invalid", False),
        ]

        for value, expected in debug_values:
            with patch.dict(os.environ, {"AWS_MCP_DEBUG": value}, clear=True):
                from aws_mcp_server.core.config import ServerConfig

                config = ServerConfig()
                assert config.debug is expected, f"Failed for value: {value}"

    def test_config_pagination_variations(self):
        """Test different pagination value variations."""
        pagination_values = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("", False),
            ("invalid", False),
        ]

        for value, expected in pagination_values:
            with patch.dict(
                os.environ, {"AWS_MCP_ENABLE_PAGINATION": value}, clear=True
            ):
                from aws_mcp_server.core.config import AWSConfig

                config = AWSConfig()
                assert config.enable_pagination is expected, (
                    f"Failed for value: {value}"
                )

    def test_config_invalid_port(self):
        """Test config with invalid port value."""
        with patch.dict(os.environ, {"AWS_MCP_PORT": "invalid"}, clear=True):
            with pytest.raises(ValueError):
                from aws_mcp_server.core.config import ServerConfig

                ServerConfig()

    def test_config_invalid_max_concurrent(self):
        """Test config with invalid max_concurrent value."""
        with patch.dict(os.environ, {"AWS_MCP_MAX_CONCURRENT": "invalid"}, clear=True):
            with pytest.raises(ValueError):
                from aws_mcp_server.core.config import AWSConfig

                AWSConfig()

    def test_config_structure(self):
        """Test that config classes have required attributes."""
        from aws_mcp_server.core.config import AWSConfig, ServerConfig

        server_config = ServerConfig()
        aws_config = AWSConfig()

        # Test that essential config attributes exist
        assert hasattr(server_config, "port")
        assert hasattr(server_config, "transport")
        assert hasattr(server_config, "debug")
        assert hasattr(aws_config, "max_concurrent")
        assert hasattr(aws_config, "enable_pagination")
        assert hasattr(aws_config, "max_results")
        assert hasattr(aws_config, "timeout_seconds")

        # Test types
        assert isinstance(server_config.port, int)
        assert isinstance(server_config.transport, str)
        assert isinstance(server_config.debug, bool)
        assert isinstance(aws_config.max_concurrent, int)
        assert isinstance(aws_config.enable_pagination, bool)
        assert isinstance(aws_config.max_results, int)
        assert isinstance(aws_config.timeout_seconds, int)

    def test_environment_case_sensitivity(self):
        """Test that environment variable names are case sensitive."""
        # Test lowercase (should not work)
        with patch.dict(os.environ, {"aws_mcp_port": "9999"}, clear=True):
            from aws_mcp_server.core.config import ServerConfig

            config = ServerConfig()
            # Should use default since lowercase env var is ignored
            assert config.port == 8888

    def test_edge_cases(self):
        """Test edge cases for configuration values."""
        # Test zero values - should raise validation error
        with patch.dict(os.environ, {"AWS_MCP_MAX_RESULTS": "0"}, clear=True):
            with pytest.raises(ValueError):
                from aws_mcp_server.core.config import AWSConfig

                AWSConfig()

        # Test very large values
        env_vars = {
            "AWS_MCP_MAX_RESULTS": "999999",
            "AWS_MCP_TIMEOUT": "3600",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            from aws_mcp_server.core.config import AWSConfig

            config = AWSConfig()

            assert config.max_results == 999999
            assert config.timeout_seconds == 3600

    def test_config_validation(self):
        """Test configuration validation."""
        # Test invalid port range
        with patch.dict(os.environ, {"AWS_MCP_PORT": "80"}, clear=True):
            with pytest.raises(ValueError):
                from aws_mcp_server.core.config import ServerConfig

                ServerConfig()

        # Test invalid transport
        with patch.dict(os.environ, {"AWS_MCP_TRANSPORT": "invalid"}, clear=True):
            with pytest.raises(ValueError):
                from aws_mcp_server.core.config import ServerConfig

                ServerConfig()
