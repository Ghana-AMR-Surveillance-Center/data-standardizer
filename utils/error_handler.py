"""
Production-ready error handling and logging system
"""

import logging
import traceback
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import streamlit as st

class ErrorHandler:
    """Centralized error handling and logging system."""
    
    def __init__(self):
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('glass_data_standardizer.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('GLASS_Data_Standardizer')
    
    def log_error(self, error: Exception, context: str = "", user_message: str = ""):
        """Log error with context and user-friendly message."""
        error_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.logger.error(f"Error ID: {error_id}")
        self.logger.error(f"Context: {context}")
        self.logger.error(f"Error: {str(error)}")
        self.logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Store error in session state for user display
        if 'error_log' not in st.session_state:
            st.session_state.error_log = []
        
        st.session_state.error_log.append({
            'id': error_id,
            'context': context,
            'error': str(error),
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message
        })
        
        return error_id
    
    def handle_file_error(self, error: Exception, filename: str, operation: str) -> str:
        """Handle file-related errors."""
        context = f"File operation failed: {operation} on {filename}"
        user_message = f"Failed to {operation} file '{filename}'. Please check the file format and try again."
        
        error_id = self.log_error(error, context, user_message)
        
        st.error(f"❌ {user_message}")
        st.error(f"Error ID: {error_id}")
        
        return error_id
    
    def handle_data_error(self, error: Exception, operation: str, data_info: str = "") -> str:
        """Handle data processing errors."""
        context = f"Data processing failed: {operation}"
        if data_info:
            context += f" - {data_info}"
        
        user_message = f"Data processing failed during {operation}. Please check your data and try again."
        
        error_id = self.log_error(error, context, user_message)
        
        st.error(f"❌ {user_message}")
        st.error(f"Error ID: {error_id}")
        
        return error_id
    
    def handle_merge_error(self, error: Exception, file1: str, file2: str) -> str:
        """Handle file merging errors."""
        context = f"File merge failed: {file1} + {file2}"
        user_message = f"Failed to merge files. Please check the file formats and column structures."
        
        error_id = self.log_error(error, context, user_message)
        
        st.error(f"❌ {user_message}")
        st.error(f"Error ID: {error_id}")
        
        return error_id
    
    def show_error_summary(self):
        """Show error summary to user."""
        if 'error_log' not in st.session_state or not st.session_state.error_log:
            return
        
        with st.expander("🔍 Error Log", expanded=False):
            for error in st.session_state.error_log[-5:]:  # Show last 5 errors
                st.error(f"**{error['timestamp']}** - {error['context']}")
                st.caption(f"Error ID: {error['id']}")
                if error['user_message']:
                    st.info(error['user_message'])
                st.divider()
    
    def clear_errors(self):
        """Clear error log."""
        if 'error_log' in st.session_state:
            st.session_state.error_log = []

# Global error handler instance
error_handler = ErrorHandler()
