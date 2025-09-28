"""
Logging Module
Provides comprehensive logging functionality for the application.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import streamlit as st

class AppLogger:
    """Centralized logging for the application."""
    
    def __init__(self, log_level: str = "INFO"):
        self.log_level = getattr(logging, log_level.upper())
        self.setup_logger()
    
    def setup_logger(self):
        """Setup the application logger."""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("glass_data_standardizer")
        self.logger.setLevel(self.log_level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler for detailed logs
        file_handler = logging.FileHandler(
            log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler for important messages
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_file_operation(self, operation: str, filename: str, success: bool, details: str = ""):
        """Log file operations."""
        status = "SUCCESS" if success else "FAILED"
        message = f"File {operation}: {filename} - {status}"
        if details:
            message += f" - {details}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)
    
    def log_data_operation(self, operation: str, rows: int, columns: int, success: bool, details: str = ""):
        """Log data operations."""
        status = "SUCCESS" if success else "FAILED"
        message = f"Data {operation}: {rows} rows, {columns} columns - {status}"
        if details:
            message += f" - {details}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)
    
    def log_user_action(self, action: str, details: str = ""):
        """Log user actions."""
        message = f"User action: {action}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def log_error(self, error: Exception, context: str = ""):
        """Log errors with context."""
        message = f"Error: {str(error)}"
        if context:
            message += f" - Context: {context}"
        self.logger.error(message, exc_info=True)
    
    def log_performance(self, operation: str, duration: float, details: str = ""):
        """Log performance metrics."""
        message = f"Performance: {operation} took {duration:.2f}s"
        if details:
            message += f" - {details}"
        self.logger.info(message)

# Global logger instance
logger = AppLogger()

def log_function_call(func):
    """Decorator to log function calls."""
    def wrapper(*args, **kwargs):
        logger.logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.log_error(e, f"Error in {func.__name__}")
            raise
    return wrapper

def log_streamlit_action(action: str, details: str = ""):
    """Log Streamlit-specific actions."""
    logger.log_user_action(f"Streamlit: {action}", details)
