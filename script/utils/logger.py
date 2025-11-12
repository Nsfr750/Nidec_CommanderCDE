"""
Logger utility for Nidec Commander CDE.

This module provides a centralized logging system that:
- Creates a new log file for each day in the 'logs' directory
- Formats log messages consistently
- Handles log rotation and cleanup
"""

import os
import logging
from logging.handlers import TimedRotatingFileHandler
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True, parents=True)

# Default log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Log levels mapping
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

def setup_logger(name: str, log_level: str = 'INFO', log_to_console: bool = True) -> logging.Logger:
    """
    Configure and return a logger with file and optional console handlers.
    
    Args:
        name: Logger name (usually __name__ of the calling module)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_console: Whether to also log to console
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVELS.get(log_level.upper(), logging.INFO))
    
    # Prevent adding handlers multiple times in case of multiple calls
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # Create logs directory if it doesn't exist
    LOG_DIR.mkdir(exist_ok=True, parents=True)
    
    # Create file handler that creates new file every day and keeps logs for 30 days
    log_file = LOG_DIR / f"nidec_commander_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',
        interval=1,
        backupCount=30,  # Keep logs for 30 days
        encoding='utf-8',
        delay=False
    )
    file_handler.setFormatter(formatter)
    file_handler.suffix = "%Y%m%d.log"
    
    # Add file handler to logger
    logger.addHandler(file_handler)
    
    # Add console handler if requested
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance with default configuration.
    
    Args:
        name: Logger name (defaults to 'nidec_commander' if None)
        
    Returns:
        Configured logger instance
    """
    return setup_logger(name or 'nidec_commander')

# Example usage
if __name__ == "__main__":
    logger = get_logger(__name__)
    logger.info("Logger initialized")
    logger.debug("This is a debug message")
    logger.warning("This is a warning")
    logger.error("This is an error")
