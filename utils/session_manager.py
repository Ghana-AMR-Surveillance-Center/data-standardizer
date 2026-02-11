"""
Session state management utilities for memory optimization
"""

import streamlit as st
import logging
from typing import List, Set, Optional
import gc

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages session state cleanup and memory optimization"""
    
    # Core session state keys that should always be preserved
    PRESERVED_KEYS = {
        'initialized',
        'workflow_selected',
        'workflow_type',
        'single_steps',
        'multiple_steps',
        'amr_steps'
    }
    
    # Data keys that can be large and should be cleaned up
    DATA_KEYS = {
        'data',
        'merged_data',
        'temp_merged_data',
        'merger_dataframes',
        'merger_files',
        'merger_info',
        'processed_data',
        'amr_data',
        'validation_results',
        'mapped_columns',
        'ast_detection_result',
        'data_format',
        'validation_result'
    }
    
    # Workflow-specific keys
    WORKFLOW_KEYS = {
        'merger_step',
        'current_file_idx',
        'show_performance_stats',
        'error_log'
    }
    
    @staticmethod
    def cleanup_workflow_data(workflow_type: Optional[str] = None):
        """
        Clean up workflow-specific data from session state.
        
        Args:
            workflow_type: Type of workflow to clean ('single', 'multiple', 'amr', or None for all)
        """
        keys_to_remove = []
        
        if workflow_type == 'single':
            keys_to_remove.extend(['data', 'mapped_columns', 'validation_results'])
        elif workflow_type == 'multiple':
            keys_to_remove.extend([
                'merged_data', 'temp_merged_data', 'merger_dataframes',
                'merger_files', 'merger_info', 'merger_step', 'current_file_idx'
            ])
        elif workflow_type == 'amr':
            keys_to_remove.extend([
                'amr_data', 'processed_data', 'ast_detection_result',
                'data_format', 'validation_result'
            ])
        else:
            # Clean all workflow data
            keys_to_remove.extend(list(SessionManager.DATA_KEYS))
            keys_to_remove.extend(list(SessionManager.WORKFLOW_KEYS))
        
        # Remove keys safely
        for key in keys_to_remove:
            if key in st.session_state:
                try:
                    del st.session_state[key]
                    logger.debug(f"Cleaned up session state key: {key}")
                except Exception as e:
                    logger.warning(f"Failed to remove session state key {key}: {str(e)}")
        
        # Force garbage collection for large objects
        gc.collect()
    
    @staticmethod
    def reset_workflow(workflow_type: Optional[str] = None):
        """
        Reset a specific workflow or all workflows.
        
        Args:
            workflow_type: Type of workflow to reset ('single', 'multiple', 'amr', or None for all)
        """
        if workflow_type == 'single':
            if 'single_steps' in st.session_state:
                for key in st.session_state['single_steps']:
                    st.session_state['single_steps'][key] = False
        elif workflow_type == 'multiple':
            if 'multiple_steps' in st.session_state:
                for key in st.session_state['multiple_steps']:
                    st.session_state['multiple_steps'][key] = False
        elif workflow_type == 'amr':
            if 'amr_steps' in st.session_state:
                for key in st.session_state['amr_steps']:
                    st.session_state['amr_steps'][key] = False
        else:
            # Reset all workflows
            for steps_key in ['single_steps', 'multiple_steps', 'amr_steps']:
                if steps_key in st.session_state:
                    for key in st.session_state[steps_key]:
                        st.session_state[steps_key][key] = False
        
        # Clean up workflow data
        SessionManager.cleanup_workflow_data(workflow_type)
    
    @staticmethod
    def get_memory_usage() -> dict:
        """
        Get estimated memory usage of session state.
        
        Returns:
            Dictionary with memory usage information
        """
        import sys
        
        total_size = 0
        key_sizes = {}
        
        for key, value in st.session_state.items():
            try:
                size = sys.getsizeof(value)
                # Try to get size of nested objects
                if hasattr(value, '__dict__'):
                    size += sys.getsizeof(value.__dict__)
                if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
                    try:
                        size += sum(sys.getsizeof(item) for item in value)
                    except:
                        pass
                
                total_size += size
                if size > 1024:  # Only track keys larger than 1KB
                    key_sizes[key] = size / 1024  # Size in KB
            except Exception:
                pass
        
        return {
            'total_mb': total_size / (1024 * 1024),
            'large_keys': dict(sorted(key_sizes.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    @staticmethod
    def cleanup_all():
        """Clean up all non-essential session state data"""
        keys_to_remove = []
        
        for key in st.session_state.keys():
            if key not in SessionManager.PRESERVED_KEYS:
                # Check if it's a data or workflow key
                if key in SessionManager.DATA_KEYS or key in SessionManager.WORKFLOW_KEYS:
                    keys_to_remove.append(key)
                # Also remove any temporary keys
                elif key.startswith('temp_') or key.startswith('_'):
                    keys_to_remove.append(key)
        
        for key in keys_to_remove:
            try:
                del st.session_state[key]
                logger.debug(f"Cleaned up session state key: {key}")
            except Exception:
                pass
        
        # Force garbage collection
        gc.collect()
        logger.info("Session state cleanup completed")

# Global session manager instance
session_manager = SessionManager()

