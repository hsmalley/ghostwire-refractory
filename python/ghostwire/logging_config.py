"""
Logging configuration for GhostWire Refractory

Implements configurable logging with support for:
- Plain text logging
- Emoji/ANSI decorated logging
- JSON structured logging
- Environment-driven opt-out for emoji decorations
"""

import json
import logging
import logging.handlers
import sys
from datetime import datetime
from enum import Enum

from .config.settings import get_settings

# Create settings instance
settings = get_settings()


class LogFormat(str, Enum):
    """Enumeration of supported log formats"""

    PLAIN = "plain"
    EMOJI = "emoji"
    JSON = "json"


class GhostWireFormatter(logging.Formatter):
    """Custom formatter supporting multiple output formats"""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    # Emoji decorators for different log levels
    EMOJIS = {
        "DEBUG": "🐛",
        "INFO": "⚡️",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "CRITICAL": "🚨",
    }

    def __init__(
        self,
        fmt: str = None,
        datefmt: str = None,
        style: str = "%",
        validate: bool = True,
        log_format: LogFormat = LogFormat.EMOJI,
        use_emoji: bool = True,
    ):
        super().__init__(fmt, datefmt, style, validate)
        self.log_format = log_format
        self.use_emoji = use_emoji

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record according to the configured format"""
        if self.log_format == LogFormat.JSON:
            return self._format_json(record)
        else:
            return self._format_text(record)

    def _format_json(self, record: logging.LogRecord) -> str:
        """Format record as JSON"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
            }:
                log_entry[key] = value

        return json.dumps(log_entry)

    def _format_text(self, record: logging.LogRecord) -> str:
        """Format record as text with optional emoji decorations"""
        # Standard text format
        base_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        # Apply color and emoji decorations if enabled
        if self.use_emoji and self.log_format == LogFormat.EMOJI:
            levelname = record.levelname
            color_start = self.COLORS.get(levelname, "")
            color_end = self.COLORS["RESET"]
            emoji = self.EMOJIS.get(levelname, "")

            decorated_format = f"{color_start}{emoji} {base_format}{color_end}"
            formatter = logging.Formatter(decorated_format, datefmt="%Y-%m-%d %H:%M:%S")
        else:
            formatter = logging.Formatter(base_format, datefmt="%Y-%m-%d %H:%M:%S")

        return formatter.format(record)


def setup_logging():
    """
    Configure the root logger according to application settings.

    Respects the following settings:
    - LOG_LEVEL: Sets the logging level
    - LOG_FILE: Optional file to write logs to
    - LOG_FORMAT: One of 'plain', 'emoji', or 'json'
    - GHOSTWIRE_NO_EMOJI: If True, disables emoji decorations regardless of LOG_FORMAT
    """
    # Get log level from settings
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Determine log format
    try:
        log_format = LogFormat(settings.LOG_FORMAT.lower())
    except ValueError:
        log_format = LogFormat.EMOJI  # Default to emoji format

    # Determine if emoji decorations should be used
    use_emoji = not settings.GHOSTWIRE_NO_EMOJI and log_format == LogFormat.EMOJI

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create formatter based on settings
    formatter = GhostWireFormatter(log_format=log_format, use_emoji=use_emoji)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Add file handler if LOG_FILE is specified
    if settings.LOG_FILE:
        file_handler = logging.handlers.RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name, applying the global configuration.

    Args:
        name: Name of the logger (typically __name__ of the module)

    Returns:
        Configured logger instance
    """
    # Make sure logging is properly configured
    if not logging.getLogger().handlers:
        setup_logging()

    return logging.getLogger(name)


# Initialize logging when module is loaded
setup_logging()
