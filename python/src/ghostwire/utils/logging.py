"""
Logging utilities for GhostWire Refractory
"""
import logging
import sys
from typing import Optional
from logging.handlers import RotatingFileHandler

from ..config.settings import settings


def setup_logging():
    """Setup application logging with proper configuration"""
    # Create a custom logger
    logger = logging.getLogger('ghostwire')
    logger.setLevel(settings.LOG_LEVEL.upper())
    
    # Remove default handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters and add them to handlers
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Create console handler with a higher log level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL.upper())
    console_handler.setFormatter(console_formatter)
    
    # Create file handler if specified
    if settings.LOG_FILE:
        file_handler = RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Add handlers to the logger
    logger.addHandler(console_handler)
    
    # Also configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL.upper())
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    if settings.LOG_FILE:
        root_logger.addHandler(file_handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance with proper configuration"""
    if name:
        logger = logging.getLogger(f'ghostwire.{name}')
    else:
        logger = logging.getLogger('ghostwire')
    
    # If logger has no handlers, set up logging
    if not logger.handlers:
        setup_logging()
    
    return logger