"""
Production-ready error handling with comprehensive logging and recovery
"""

import logging
import traceback
import sys
from datetime import datetime
from typing import Optional, Dict, Any, Callable
import functools
import streamlit as st

logger = logging.getLogger(__name__)


class ProductionErrorHandler:
    """Production-grade error handling with recovery strategies"""
    
    def __init__(self, production_logger=None):
        self.production_logger = production_logger
        self.error_counts = {}
        self.max_errors_per_minute = 10
        
    def handle_error(self, error: Exception, context: str = "", 
                    user_message: str = "", severity: str = "error",
                    recovery_action: Optional[Callable] = None) -> str:
        """
        Handle error with comprehensive logging and optional recovery
        
        Args:
            error: The exception that occurred
            context: Context where error occurred
            user_message: User-friendly error message
            severity: 'error', 'warning', 'critical'
            recovery_action: Optional function to attempt recovery
            
        Returns:
            Error ID for tracking
        """
        error_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # Rate limiting - prevent error spam
        if self._should_throttle_error(context):
            logger.warning(f"Error throttled: {context}")
            return error_id
        
        # Log to production logger if available
        if self.production_logger:
            try:
                self.production_logger.log_error(
                    error=error,
                    context=context,
                    user_id=None,  # Could be extracted from session
                    request_id=error_id
                )
            except Exception as log_error:
                logger.error(f"Failed to log to production logger: {log_error}")
        
        # Log to standard logger
        logger.error(f"[{error_id}] {context}: {str(error)}")
        logger.debug(f"[{error_id}] Traceback:\n{traceback.format_exc()}")
        
        # Attempt recovery if provided
        if recovery_action:
            try:
                recovery_result = recovery_action()
                if recovery_result:
                    logger.info(f"[{error_id}] Recovery action succeeded")
                    return error_id
            except Exception as recovery_error:
                logger.error(f"[{error_id}] Recovery action failed: {recovery_error}")
        
        # Display user-friendly error
        if user_message:
            st.error(f"❌ {user_message}")
            if severity == "critical":
                st.error(f"⚠️ Error ID: {error_id}. Please contact support if this persists.")
        
        return error_id
    
    def _should_throttle_error(self, context: str) -> bool:
        """Check if error should be throttled to prevent spam"""
        current_minute = datetime.now().strftime("%Y%m%d%H%M")
        key = f"{context}_{current_minute}"
        
        count = self.error_counts.get(key, 0)
        if count >= self.max_errors_per_minute:
            return True
        
        self.error_counts[key] = count + 1
        return False
    
    def handle_file_error(self, error: Exception, filename: str, 
                         operation: str, recovery_action: Optional[Callable] = None) -> str:
        """Handle file-related errors with context"""
        context = f"File operation: {operation} on {filename}"
        user_message = f"Failed to {operation} file '{filename}'. Please check the file format and try again."
        
        return self.handle_error(
            error=error,
            context=context,
            user_message=user_message,
            severity="error",
            recovery_action=recovery_action
        )
    
    def handle_data_error(self, error: Exception, operation: str, 
                         data_info: str = "", recovery_action: Optional[Callable] = None) -> str:
        """Handle data processing errors"""
        context = f"Data processing: {operation}"
        if data_info:
            context += f" - {data_info}"
        
        user_message = f"Data processing failed during {operation}. Please check your data and try again."
        
        return self.handle_error(
            error=error,
            context=context,
            user_message=user_message,
            severity="error",
            recovery_action=recovery_action
        )
    
    def handle_validation_error(self, error: Exception, field: str = "", 
                               validation_type: str = "") -> str:
        """Handle data validation errors"""
        context = f"Validation error: {validation_type}"
        if field:
            context += f" on field '{field}'"
        
        user_message = f"Data validation failed. Please check your input and try again."
        
        return self.handle_error(
            error=error,
            context=context,
            user_message=user_message,
            severity="warning"
        )
    
    def safe_execute(self, func: Callable, context: str = "", 
                    default_return=None, recovery_action: Optional[Callable] = None):
        """
        Safely execute a function with error handling
        
        Args:
            func: Function to execute
            context: Context description
            default_return: Value to return on error
            recovery_action: Optional recovery function
            
        Returns:
            Function result or default_return on error
        """
        try:
            return func()
        except Exception as e:
            self.handle_error(
                error=e,
                context=f"Execution error in {context}",
                user_message=f"An error occurred: {str(e)}",
                recovery_action=recovery_action
            )
            return default_return


def production_error_handler(func: Callable):
    """Decorator for production error handling"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        handler = ProductionErrorHandler()
        try:
            return func(*args, **kwargs)
        except Exception as e:
            handler.handle_error(
                error=e,
                context=f"Function: {func.__name__}",
                user_message=f"An error occurred in {func.__name__}",
                severity="error"
            )
            raise
    return wrapper

