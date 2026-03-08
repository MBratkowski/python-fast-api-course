"""
Exercise 1: Configure Python Logging

In this exercise, you'll configure Python's stdlib logging module with
proper handlers, formatters, and log levels.

Your task:
1. Implement configure_logging() that creates a logger with:
   - A StreamHandler attached to a given stream
   - Handler level set to INFO
   - A Formatter with the pattern: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
   - The logger's own level set to DEBUG (so the handler does the filtering)

2. The function should return the configured logger.

Mobile analogy: This is like configuring os.Logger on iOS with specific
subsystem/category settings, or setting up Timber with a custom Tree on Android.

Run: pytest 021-logging-monitoring/exercises/01_logging_config.py -v
"""

import io
import logging


# ============= TODO: Implement configure_logging =============
# Create a function that:
# 1. Creates a logger with the given name using logging.getLogger()
# 2. Sets the logger level to DEBUG
# 3. Creates a StreamHandler that writes to the given stream
# 4. Sets the handler level to INFO
# 5. Creates a Formatter with pattern: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
# 6. Attaches the formatter to the handler
# 7. Adds the handler to the logger
# 8. Returns the logger
#
# Hints:
# - logging.StreamHandler(stream) creates a handler that writes to a stream
# - handler.setLevel() sets the minimum level the handler will process
# - handler.setFormatter() attaches a formatter to the handler
# - logger.addHandler() attaches a handler to the logger


def configure_logging(name: str, stream: io.StringIO) -> logging.Logger:
    """Configure a logger with a StreamHandler and Formatter.

    Args:
        name: The logger name (e.g., "myapp")
        stream: The stream to write log output to (e.g., io.StringIO for testing)

    Returns:
        A configured logging.Logger instance
    """
    # TODO: Implement this function
    pass


# ============= TESTS (do not modify below) =============


class TestLoggingConfig:
    """Tests that validate your logging configuration."""

    def _make_logger(self) -> tuple[logging.Logger, io.StringIO]:
        """Helper to create a logger with a fresh stream."""
        stream = io.StringIO()
        logger = configure_logging("test_app", stream)
        return logger, stream

    def test_returns_logger(self):
        """configure_logging should return a logging.Logger instance."""
        stream = io.StringIO()
        logger = configure_logging("test_returns", stream)
        assert isinstance(logger, logging.Logger), (
            "configure_logging should return a logging.Logger instance"
        )

    def test_logger_has_correct_name(self):
        """Logger should have the name passed to configure_logging."""
        stream = io.StringIO()
        logger = configure_logging("my_custom_name", stream)
        assert logger.name == "my_custom_name", (
            f"Expected logger name 'my_custom_name', got '{logger.name}'"
        )

    def test_logger_has_handler(self):
        """Logger should have at least one handler attached."""
        logger, stream = self._make_logger()
        assert len(logger.handlers) >= 1, (
            "Logger should have at least one handler. "
            "Use logger.addHandler() to attach a StreamHandler."
        )

    def test_handler_is_stream_handler(self):
        """The handler should be a StreamHandler."""
        logger, stream = self._make_logger()
        stream_handlers = [
            h for h in logger.handlers
            if isinstance(h, logging.StreamHandler)
        ]
        assert len(stream_handlers) >= 1, (
            "Logger should have a StreamHandler. "
            "Use logging.StreamHandler(stream) to create one."
        )

    def test_handler_level_is_info(self):
        """The StreamHandler should have its level set to INFO."""
        logger, stream = self._make_logger()
        handler = logger.handlers[0]
        assert handler.level == logging.INFO, (
            f"Handler level should be INFO (20), got {handler.level}. "
            "Use handler.setLevel(logging.INFO)."
        )

    def test_handler_has_formatter(self):
        """The handler should have a Formatter attached."""
        logger, stream = self._make_logger()
        handler = logger.handlers[0]
        assert handler.formatter is not None, (
            "Handler should have a Formatter. "
            "Use handler.setFormatter(logging.Formatter(...))."
        )

    def test_formatter_includes_level(self):
        """The formatter should include the log level in output."""
        logger, stream = self._make_logger()
        logger.info("test message")
        output = stream.getvalue()
        assert "INFO" in output, (
            f"Log output should include the level name 'INFO'. Got: {output!r}"
        )

    def test_formatter_includes_name(self):
        """The formatter should include the logger name in output."""
        stream = io.StringIO()
        logger = configure_logging("my_app", stream)
        logger.info("test message")
        output = stream.getvalue()
        assert "my_app" in output, (
            f"Log output should include the logger name 'my_app'. Got: {output!r}"
        )

    def test_formatter_includes_message(self):
        """The formatter should include the actual log message."""
        logger, stream = self._make_logger()
        logger.info("hello world")
        output = stream.getvalue()
        assert "hello world" in output, (
            f"Log output should include the message 'hello world'. Got: {output!r}"
        )

    def test_info_messages_appear(self):
        """INFO messages should appear in the output (handler level is INFO)."""
        logger, stream = self._make_logger()
        logger.info("info message")
        output = stream.getvalue()
        assert "info message" in output, (
            "INFO messages should appear in the output. "
            "Make sure the handler level is set to INFO or lower."
        )

    def test_debug_messages_filtered(self):
        """DEBUG messages should NOT appear (handler level is INFO)."""
        logger, stream = self._make_logger()
        logger.debug("debug message")
        output = stream.getvalue()
        assert "debug message" not in output, (
            "DEBUG messages should NOT appear in the output. "
            "The handler level should be INFO, which filters out DEBUG."
        )

    def test_warning_messages_appear(self):
        """WARNING messages should appear (above INFO level)."""
        logger, stream = self._make_logger()
        logger.warning("warning message")
        output = stream.getvalue()
        assert "warning message" in output, (
            "WARNING messages should appear in the output."
        )

    def test_error_messages_appear(self):
        """ERROR messages should appear (above INFO level)."""
        logger, stream = self._make_logger()
        logger.error("error message")
        output = stream.getvalue()
        assert "error message" in output, (
            "ERROR messages should appear in the output."
        )
