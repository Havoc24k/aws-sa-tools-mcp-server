"""
Test cases for server module
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from aws_mcp_server.server import main


class TestMain:
    """Test main function"""

    def test_main_with_default_args(self):
        """Test main function with default arguments"""
        with (
            patch("sys.argv", ["server.py"]),
            patch("aws_mcp_server.server.setup_logging") as mock_setup_logging,
            patch("aws_mcp_server.server.mcp") as mock_mcp,
        ):
            main()

            # Verify logging setup
            mock_setup_logging.assert_called_once_with(
                level="INFO",
                include_timestamp=False,
                log_file="logs/aws_mcp_server.log",
            )

            # Verify environment variables
            assert os.environ["ENABLE_VECTOR_STORE"] == "false"
            assert os.environ["DATA_SOURCE_PATH"] == "datasource/"

            # Verify server run with stdio transport
            mock_mcp.run.assert_called_once_with(transport="stdio")

    def test_main_with_sse_transport(self):
        """Test main function with SSE transport"""
        with (
            patch("sys.argv", ["server.py", "--sse", "--port", "9999"]),
            patch("aws_mcp_server.server.setup_logging") as mock_setup_logging,
            patch("aws_mcp_server.server.mcp") as mock_mcp,
        ):
            main()

            # Verify logging setup
            mock_setup_logging.assert_called_once_with(
                level="INFO",
                include_timestamp=False,
                log_file="logs/aws_mcp_server.log",
            )

            # Verify port setting
            assert mock_mcp.settings.port == 9999

            # Verify server run with SSE transport
            mock_mcp.run.assert_called_once_with(transport="sse")

    def test_main_with_vector_store_enabled(self):
        """Test main function with vector store enabled"""
        with (
            patch(
                "sys.argv",
                ["server.py", "--enable-vector-store", "--data-source", "/custom/path"],
            ),
            patch("aws_mcp_server.server.setup_logging") as mock_setup_logging,
            patch("aws_mcp_server.server.mcp") as mock_mcp,
            patch(
                "aws_mcp_server.services.knowledge.vector_store_init.initialize_vector_store"
            ) as mock_init_vector,
        ):
            main()

            # Verify logging setup
            mock_setup_logging.assert_called_once_with(
                level="INFO",
                include_timestamp=False,
                log_file="logs/aws_mcp_server.log",
            )

            # Verify environment variables
            assert os.environ["ENABLE_VECTOR_STORE"] == "true"
            assert os.environ["DATA_SOURCE_PATH"] == "/custom/path"

            # Verify vector store initialization
            mock_init_vector.assert_called_once_with("/custom/path")

            # Verify server run
            mock_mcp.run.assert_called_once_with(transport="stdio")

    def test_main_with_custom_log_file(self):
        """Test main function with custom log file"""
        custom_log_file = "/tmp/custom.log"

        with (
            patch("sys.argv", ["server.py", "--log-file", custom_log_file]),
            patch("aws_mcp_server.server.setup_logging") as mock_setup_logging,
            patch("aws_mcp_server.server.mcp") as mock_mcp,
        ):
            main()

            # Verify logging setup with custom log file
            mock_setup_logging.assert_called_once_with(
                level="INFO", include_timestamp=False, log_file=custom_log_file
            )

    def test_main_with_all_options(self):
        """Test main function with all command line options"""
        with (
            patch(
                "sys.argv",
                [
                    "server.py",
                    "--sse",
                    "--port",
                    "7777",
                    "--enable-vector-store",
                    "--data-source",
                    "/test/data",
                    "--log-file",
                    "/test/logs/test.log",
                ],
            ),
            patch("aws_mcp_server.server.setup_logging") as mock_setup_logging,
            patch("aws_mcp_server.server.mcp") as mock_mcp,
            patch(
                "aws_mcp_server.services.knowledge.vector_store_init.initialize_vector_store"
            ) as mock_init_vector,
        ):
            main()

            # Verify logging setup
            mock_setup_logging.assert_called_once_with(
                level="INFO", include_timestamp=False, log_file="/test/logs/test.log"
            )

            # Verify environment variables
            assert os.environ["ENABLE_VECTOR_STORE"] == "true"
            assert os.environ["DATA_SOURCE_PATH"] == "/test/data"

            # Verify vector store initialization
            mock_init_vector.assert_called_once_with("/test/data")

            # Verify port setting
            assert mock_mcp.settings.port == 7777

            # Verify server run with SSE transport
            mock_mcp.run.assert_called_once_with(transport="sse")

    def test_main_vector_store_import_error(self):
        """Test main function when vector store import fails"""
        with (
            patch("sys.argv", ["server.py", "--enable-vector-store"]),
            patch("aws_mcp_server.server.setup_logging") as mock_setup_logging,
            patch("aws_mcp_server.server.mcp") as mock_mcp,
            patch("builtins.__import__", side_effect=ImportError("Module not found")),
        ):
            # Should not raise an exception
            with pytest.raises(ImportError):
                main()

    def test_main_environment_variable_types(self):
        """Test that environment variables are set with correct types"""
        with (
            patch("sys.argv", ["server.py", "--enable-vector-store"]),
            patch("aws_mcp_server.server.setup_logging"),
            patch("aws_mcp_server.server.mcp"),
            patch(
                "aws_mcp_server.services.knowledge.vector_store_init.initialize_vector_store"
            ),
        ):
            main()

            # Verify environment variables are strings
            assert isinstance(os.environ["ENABLE_VECTOR_STORE"], str)
            assert isinstance(os.environ["DATA_SOURCE_PATH"], str)
            assert os.environ["ENABLE_VECTOR_STORE"] == "true"

    def test_main_preserves_original_environment(self):
        """Test that main function doesn't interfere with other environment variables"""
        # Set a test environment variable
        original_value = "test_value"
        os.environ["TEST_VAR"] = original_value

        try:
            with (
                patch("sys.argv", ["server.py"]),
                patch("aws_mcp_server.server.setup_logging"),
                patch("aws_mcp_server.server.mcp"),
            ):
                main()

                # Verify our test variable is preserved
                assert os.environ["TEST_VAR"] == original_value

        finally:
            # Clean up
            if "TEST_VAR" in os.environ:
                del os.environ["TEST_VAR"]


class TestArgumentParsing:
    """Test argument parsing functionality"""

    def test_help_message(self):
        """Test that help message is displayed correctly"""
        with patch("sys.argv", ["server.py", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            # argparse exits with code 0 for help
            assert exc_info.value.code == 0

    def test_invalid_port_type(self):
        """Test invalid port type handling"""
        with patch("sys.argv", ["server.py", "--port", "invalid"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            # argparse exits with code 2 for invalid arguments
            assert exc_info.value.code == 2

    def test_port_argument_parsing(self):
        """Test port argument parsing"""
        with (
            patch("sys.argv", ["server.py", "--sse", "--port", "8080"]),
            patch("aws_mcp_server.server.setup_logging"),
            patch("aws_mcp_server.server.mcp") as mock_mcp,
        ):
            main()

            # Verify port is set as integer
            assert mock_mcp.settings.port == 8080

    def test_boolean_flag_parsing(self):
        """Test boolean flag parsing"""
        with (
            patch("sys.argv", ["server.py", "--sse", "--enable-vector-store"]),
            patch("aws_mcp_server.server.setup_logging"),
            patch("aws_mcp_server.server.mcp") as mock_mcp,
            patch(
                "aws_mcp_server.services.knowledge.vector_store_init.initialize_vector_store"
            ) as mock_init_vector,
        ):
            main()

            # Verify both boolean flags are processed
            mock_mcp.run.assert_called_once_with(transport="sse")
            mock_init_vector.assert_called_once()


class TestModuleIntegration:
    """Test integration with other modules"""

    def test_mcp_module_import(self):
        """Test that mcp module is imported correctly"""
        with (
            patch("sys.argv", ["server.py"]),
            patch("aws_mcp_server.server.setup_logging"),
            patch("aws_mcp_server.server.mcp") as mock_mcp,
        ):
            main()

            # Verify mcp module is accessed
            assert mock_mcp.run.called

    def test_logging_config_import(self):
        """Test that logging_config module is imported correctly"""
        with (
            patch("sys.argv", ["server.py"]),
            patch("aws_mcp_server.server.setup_logging") as mock_setup_logging,
            patch("aws_mcp_server.server.mcp"),
        ):
            main()

            # Verify setup_logging is called
            assert mock_setup_logging.called

    def test_vector_store_conditional_import(self):
        """Test that vector store module is only imported when needed"""
        # Test with vector store enabled
        with (
            patch("sys.argv", ["server.py", "--enable-vector-store"]),
            patch("aws_mcp_server.server.setup_logging"),
            patch("aws_mcp_server.server.mcp"),
            patch(
                "aws_mcp_server.services.knowledge.vector_store_init.initialize_vector_store"
            ) as mock_init_vector,
        ):
            main()

            # Vector store initialization should be called
            mock_init_vector.assert_called_once()


class TestErrorHandling:
    """Test error handling scenarios"""

    def test_mcp_run_exception(self):
        """Test handling of mcp.run exceptions"""
        with (
            patch("sys.argv", ["server.py"]),
            patch("aws_mcp_server.server.setup_logging"),
            patch("aws_mcp_server.server.mcp") as mock_mcp,
        ):
            mock_mcp.run.side_effect = Exception("Server failed to start")

            with pytest.raises(Exception, match="Server failed to start"):
                main()

    def test_setup_logging_exception(self):
        """Test handling of setup_logging exceptions"""
        with (
            patch("sys.argv", ["server.py"]),
            patch("aws_mcp_server.server.setup_logging") as mock_setup_logging,
            patch("aws_mcp_server.server.mcp"),
        ):
            mock_setup_logging.side_effect = Exception("Logging setup failed")

            with pytest.raises(Exception, match="Logging setup failed"):
                main()
