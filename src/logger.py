"""
Logging Setup for TradeGenius AI
Provides consistent logging across all modules
"""

import logging
import logging.handlers
import os
import sys


_initialized = False


def setup_logging(level: str = 'INFO', log_file: str = 'tradegenius.log',
                  max_bytes: int = 5242880, backup_count: int = 3):
    """
    Setup application-wide logging with both console and file handlers.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file
        max_bytes: Max log file size before rotation (default 5MB)
        backup_count: Number of backup log files to keep
    """
    global _initialized
    if _initialized:
        return

    # Try to load from config
    try:
        from . import config as cfg
        log_config = cfg.get('logging')
        if log_config:
            level = log_config.get('level', level)
            log_file = log_config.get('file', log_file)
            max_bytes = log_config.get('max_bytes', max_bytes)
            backup_count = log_config.get('backup_count', backup_count)
    except (ImportError, Exception):
        pass

    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Root logger
    root_logger = logging.getLogger('tradegenius')
    root_logger.setLevel(numeric_level)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(max(numeric_level, logging.INFO))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except (PermissionError, OSError) as e:
        root_logger.warning(f"Could not create log file {log_file}: {e}")

    _initialized = True
    root_logger.info("TradeGenius AI logging initialized")


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger for a module.

    Args:
        name: Module name (e.g., 'data_loader', 'advanced_ai')

    Returns:
        Logger instance
    """
    if not _initialized:
        setup_logging()
    return logging.getLogger(f'tradegenius.{name}')
