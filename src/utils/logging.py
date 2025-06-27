"""
Logging configuration for the GenAI Email Processing System.
"""

import sys
from pathlib import Path
from loguru import logger
from src.config.settings import settings


def setup_logging():
    """Configure logging for the application."""
    
    # Remove default handler
    logger.remove()
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Console handler
    if settings.LOG_FORMAT == "json":
        console_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    else:
        console_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    
    logger.add(
        sys.stdout,
        format=console_format,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # File handler for all logs
    logger.add(
        logs_dir / "application.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="1 day",
        retention="30 days",
        compression="gz",
        backtrace=True,
        diagnose=True
    )
    
    # Separate file handler for errors
    logger.add(
        logs_dir / "errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="1 week",
        retention="12 weeks",
        compression="gz",
        backtrace=True,
        diagnose=True
    )
    
    # Log application startup
    logger.info(f"Logging configured - Level: {settings.LOG_LEVEL}, Format: {settings.LOG_FORMAT}")


def get_logger(name: str):
    """Get a logger instance for a specific module."""
    return logger.bind(name=name)
