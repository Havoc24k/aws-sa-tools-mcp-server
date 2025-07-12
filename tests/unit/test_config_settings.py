"""Unit tests for simplified configuration settings."""

import os
from unittest.mock import patch

import pytest


class TestSimplifiedSettings:
    """Test simplified configuration settings."""

    def test_settings_defaults(self):
        """Test that default settings are loaded correctly."""
        with patch.dict(os.environ, {}, clear=True):
            import importlib

            from aws_mcp_server.config import settings as settings_module

            importlib.reload(settings_module)

            # Test default values
            assert settings_module.DEFAULT_PORT == 8888
            assert settings_module.DEFAULT_TRANSPORT == "stdio"
            assert settings_module.DEBUG is False
            assert settings_module.MAX_CONCURRENT_REQUESTS == 10
            assert settings_module.ENABLE_PAGINATION is True
            assert settings_module.DEFAULT_MAX_RESULTS == 1000
            assert settings_module.DEFAULT_TIMEOUT_SECONDS == 30

    def test_settings_from_environment_variables(self):
        """Test that settings can be overridden by environment variables."""
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
            import importlib

            from aws_mcp_server.config import settings as settings_module

            importlib.reload(settings_module)

            assert settings_module.DEFAULT_PORT == 9999
            assert settings_module.DEFAULT_TRANSPORT == "sse"
            assert settings_module.DEBUG is True
            assert settings_module.MAX_CONCURRENT_REQUESTS == 20
            assert settings_module.ENABLE_PAGINATION is False
            assert settings_module.DEFAULT_MAX_RESULTS == 2000
            assert settings_module.DEFAULT_TIMEOUT_SECONDS == 60

    def test_settings_debug_variations(self):
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
                import importlib

                from aws_mcp_server.config import settings as settings_module

                importlib.reload(settings_module)
                assert settings_module.DEBUG is expected, f"Failed for value: {value}"

    def test_settings_pagination_variations(self):
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
                import importlib

                from aws_mcp_server.config import settings as settings_module

                importlib.reload(settings_module)
                assert settings_module.ENABLE_PAGINATION is expected, (
                    f"Failed for value: {value}"
                )

    def test_settings_invalid_port(self):
        """Test settings with invalid port value."""
        with patch.dict(os.environ, {"AWS_MCP_PORT": "invalid"}, clear=True):
            with pytest.raises(ValueError):
                import importlib

                from aws_mcp_server.config import settings as settings_module

                importlib.reload(settings_module)

    def test_settings_invalid_max_concurrent(self):
        """Test settings with invalid max_concurrent value."""
        with patch.dict(os.environ, {"AWS_MCP_MAX_CONCURRENT": "invalid"}, clear=True):
            with pytest.raises(ValueError):
                import importlib

                from aws_mcp_server.config import settings as settings_module

                importlib.reload(settings_module)

    def test_constants_structure(self):
        """Test that required constants exist."""
        from aws_mcp_server.config import settings as settings_module

        # Test that essential settings exist
        assert hasattr(settings_module, "DEFAULT_PORT")
        assert hasattr(settings_module, "DEFAULT_TRANSPORT")
        assert hasattr(settings_module, "DEBUG")
        assert hasattr(settings_module, "MAX_CONCURRENT_REQUESTS")
        assert hasattr(settings_module, "ENABLE_PAGINATION")
        assert hasattr(settings_module, "DEFAULT_MAX_RESULTS")
        assert hasattr(settings_module, "DEFAULT_TIMEOUT_SECONDS")

        # Test types
        assert isinstance(settings_module.DEFAULT_PORT, int)
        assert isinstance(settings_module.DEFAULT_TRANSPORT, str)
        assert isinstance(settings_module.DEBUG, bool)
        assert isinstance(settings_module.MAX_CONCURRENT_REQUESTS, int)
        assert isinstance(settings_module.ENABLE_PAGINATION, bool)
        assert isinstance(settings_module.DEFAULT_MAX_RESULTS, int)
        assert isinstance(settings_module.DEFAULT_TIMEOUT_SECONDS, int)

    def test_environment_case_sensitivity(self):
        """Test that environment variable names are case sensitive."""
        # Test lowercase (should not work)
        with patch.dict(os.environ, {"aws_mcp_port": "9999"}, clear=True):
            import importlib

            from aws_mcp_server.config import settings as settings_module

            importlib.reload(settings_module)
            # Should use default since lowercase env var is ignored
            assert settings_module.DEFAULT_PORT == 8888

    def test_edge_cases(self):
        """Test edge cases for configuration values."""
        # Test zero values
        env_vars = {
            "AWS_MCP_MAX_RESULTS": "0",
            "AWS_MCP_TIMEOUT": "0",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            import importlib

            from aws_mcp_server.config import settings as settings_module

            importlib.reload(settings_module)

            assert settings_module.DEFAULT_MAX_RESULTS == 0
            assert settings_module.DEFAULT_TIMEOUT_SECONDS == 0

        # Test very large values
        env_vars = {
            "AWS_MCP_MAX_RESULTS": "999999",
            "AWS_MCP_TIMEOUT": "3600",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            import importlib

            from aws_mcp_server.config import settings as settings_module

            importlib.reload(settings_module)

            assert settings_module.DEFAULT_MAX_RESULTS == 999999
            assert settings_module.DEFAULT_TIMEOUT_SECONDS == 3600
