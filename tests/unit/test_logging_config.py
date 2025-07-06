"""
Test cases for logging configuration
"""

import logging
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from aws_mcp_server.logging_config import get_logger, setup_logging


class TestSetupLogging:
    """Test setup_logging function"""

    def test_setup_logging_defaults(self):
        """Test setup_logging with default parameters"""
        logger = setup_logging()

        assert logger.name == "aws_mcp_server"
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        assert not logger.propagate

    def test_setup_logging_custom_level(self):
        """Test setup_logging with custom log level"""
        logger = setup_logging(level="DEBUG")

        assert logger.level == logging.DEBUG
        assert logger.handlers[0].level == logging.DEBUG

    def test_setup_logging_custom_format(self):
        """Test setup_logging with custom format string"""
        custom_format = "%(levelname)s: %(message)s"
        logger = setup_logging(format_string=custom_format)

        formatter = logger.handlers[0].formatter
        assert formatter._fmt == custom_format

    def test_setup_logging_with_timestamp(self):
        """Test setup_logging with timestamp enabled"""
        logger = setup_logging(include_timestamp=True)

        formatter = logger.handlers[0].formatter
        assert "%(asctime)s" in formatter._fmt

    def test_setup_logging_without_timestamp(self):
        """Test setup_logging with timestamp disabled"""
        logger = setup_logging(include_timestamp=False)

        formatter = logger.handlers[0].formatter
        assert "%(asctime)s" not in formatter._fmt

    def test_setup_logging_file_handler(self):
        """Test setup_logging with file handler"""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp:
            log_file = tmp.name

        try:
            logger = setup_logging(log_file=log_file)

            # Should have both console and file handlers
            assert len(logger.handlers) == 2

            # Check handler types
            handler_types = [type(h).__name__ for h in logger.handlers]
            assert "StreamHandler" in handler_types
            assert "RotatingFileHandler" in handler_types

        finally:
            Path(log_file).unlink(missing_ok=True)

    def test_setup_logging_file_handler_creates_directory(self):
        """Test that setup_logging creates log directory if it doesn't exist"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_file = Path(tmp_dir) / "logs" / "test.log"

            # Directory doesn't exist initially
            assert not log_file.parent.exists()

            setup_logging(log_file=str(log_file))

            # Directory should be created
            assert log_file.parent.exists()

    def test_setup_logging_file_handler_custom_rotation(self):
        """Test setup_logging with custom rotation parameters"""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp:
            log_file = tmp.name

        try:
            max_bytes = 1024
            backup_count = 3

            logger = setup_logging(
                log_file=log_file, max_bytes=max_bytes, backup_count=backup_count
            )

            # Find the rotating file handler
            rotating_handler = None
            for handler in logger.handlers:
                if hasattr(handler, "maxBytes"):
                    rotating_handler = handler
                    break

            assert rotating_handler is not None
            assert rotating_handler.maxBytes == max_bytes
            assert rotating_handler.backupCount == backup_count

        finally:
            Path(log_file).unlink(missing_ok=True)

    def test_setup_logging_removes_existing_handlers(self):
        """Test that setup_logging removes existing handlers"""
        # First setup
        logger1 = setup_logging()
        initial_handler_count = len(logger1.handlers)

        # Second setup should replace handlers, not add to them
        logger2 = setup_logging()

        # Should be the same logger instance
        assert logger1 is logger2
        # Should have same number of handlers as initial setup
        assert len(logger2.handlers) == initial_handler_count

    def test_setup_logging_file_timestamp_format(self):
        """Test that file handler uses timestamp format"""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp:
            log_file = tmp.name

        try:
            logger = setup_logging(log_file=log_file, include_timestamp=False)

            # Find file handler
            file_handler = None
            for handler in logger.handlers:
                if hasattr(handler, "baseFilename"):
                    file_handler = handler
                    break

            assert file_handler is not None
            # File handler should use timestamp even when console doesn't
            assert "%(asctime)s" in file_handler.formatter._fmt

        finally:
            Path(log_file).unlink(missing_ok=True)

    def test_setup_logging_invalid_level(self):
        """Test setup_logging with invalid log level"""
        with pytest.raises(AttributeError):
            setup_logging(level="INVALID_LEVEL")

    def test_setup_logging_writes_to_file(self):
        """Test that logging actually writes to file"""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp:
            log_file = tmp.name

        try:
            logger = setup_logging(log_file=log_file)
            test_message = "Test log message"

            logger.info(test_message)

            # Read file content
            with open(log_file) as f:
                content = f.read()

            assert test_message in content

        finally:
            Path(log_file).unlink(missing_ok=True)


class TestGetLogger:
    """Test get_logger function"""

    def test_get_logger_default_name(self):
        """Test get_logger with default name"""
        logger = get_logger()

        assert logger.name == "aws_mcp_server"
        assert isinstance(logger, logging.Logger)

    def test_get_logger_custom_name(self):
        """Test get_logger with custom name"""
        custom_name = "test_logger"
        logger = get_logger(custom_name)

        assert logger.name == custom_name
        assert isinstance(logger, logging.Logger)

    def test_get_logger_returns_same_instance(self):
        """Test that get_logger returns the same instance for same name"""
        logger1 = get_logger("test")
        logger2 = get_logger("test")

        assert logger1 is logger2

    def test_get_logger_different_names_different_instances(self):
        """Test that get_logger returns different instances for different names"""
        logger1 = get_logger("test1")
        logger2 = get_logger("test2")

        assert logger1 is not logger2
        assert logger1.name != logger2.name


class TestLoggingIntegration:
    """Integration tests for logging functionality"""

    def test_console_output(self):
        """Test that console logging produces expected output"""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            logger = setup_logging(level="INFO", include_timestamp=False)
            test_message = "Test console message"

            logger.info(test_message)

            output = mock_stdout.getvalue()
            assert "INFO" in output
            assert test_message in output

    def test_different_log_levels(self):
        """Test different log levels"""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            logger = setup_logging(level="DEBUG", include_timestamp=False)

            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            logger.critical("Critical message")

            output = mock_stdout.getvalue()
            assert "DEBUG" in output
            assert "INFO" in output
            assert "WARNING" in output
            assert "ERROR" in output
            assert "CRITICAL" in output

    def test_log_level_filtering(self):
        """Test that log level filtering works correctly"""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            logger = setup_logging(level="WARNING", include_timestamp=False)

            logger.debug("Debug message")  # Should not appear
            logger.info("Info message")  # Should not appear
            logger.warning("Warning message")  # Should appear
            logger.error("Error message")  # Should appear

            output = mock_stdout.getvalue()
            assert "Debug message" not in output
            assert "Info message" not in output
            assert "Warning message" in output
            assert "Error message" in output

    def test_file_and_console_logging_together(self):
        """Test that both file and console logging work simultaneously"""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp:
            log_file = tmp.name

        try:
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                logger = setup_logging(log_file=log_file, include_timestamp=False)
                test_message = "Test dual logging"

                logger.info(test_message)

                # Check console output
                console_output = mock_stdout.getvalue()
                assert test_message in console_output

                # Check file output
                with open(log_file) as f:
                    file_content = f.read()
                assert test_message in file_content

        finally:
            Path(log_file).unlink(missing_ok=True)

    def test_logger_hierarchy(self):
        """Test that logger hierarchy works correctly"""
        # Set up parent logger
        parent_logger = setup_logging()

        # Get child logger
        child_logger = get_logger("aws_mcp_server.child")

        # Child should inherit from parent but not propagate
        assert child_logger.name.startswith(parent_logger.name)
        # Parent logger should have propagate=False
        assert not parent_logger.propagate
