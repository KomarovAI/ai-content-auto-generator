#!/usr/bin/env python3
"""
Logger - Centralized logging configuration
"""

import sys
from pathlib import Path
from loguru import logger


def setup_logger(config: dict = None):
    """
    Setup centralized logging for the application.
    
    Args:
        config: Logging configuration from config.yaml
    """
    # Remove default handler
    logger.remove()
    
    # Default config
    if config is None:
        config = {
            'level': 'INFO',
            'file': 'logs/generator.log',
            'rotation': '10 MB',
            'retention': '30 days',
            'format': '{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}'
        }
    
    log_format = config.get('format', 
        '{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}')
    log_level = config.get('level', 'INFO')
    
    # Console handler
    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level,
        colorize=True
    )
    
    # File handler
    log_file = config.get('file', 'logs/generator.log')
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_file,
        format=log_format,
        level=log_level,
        rotation=config.get('rotation', '10 MB'),
        retention=config.get('retention', '30 days'),
        compression='zip'
    )
    
    logger.info("Logger initialized successfully")
    return logger


# Convenience functions for different log levels
def debug(message: str, **kwargs):
    """Log debug message."""
    logger.debug(message, **kwargs)


def info(message: str, **kwargs):
    """Log info message."""
    logger.info(message, **kwargs)


def warning(message: str, **kwargs):
    """Log warning message."""
    logger.warning(message, **kwargs)


def error(message: str, **kwargs):
    """Log error message."""
    logger.error(message, **kwargs)


def critical(message: str, **kwargs):
    """Log critical message."""
    logger.critical(message, **kwargs)


if __name__ == "__main__":
    # Test logger
    setup_logger()
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")