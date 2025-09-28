"""
State management utilities for the file merger application.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

import streamlit as st


class StateManager:
    """Manages application state persistence and recovery."""
    
    SAVE_FILE = ".merger_state.json"
    
    @staticmethod
    def save_state(data: Dict[str, Any]) -> None:
        """Save current state to a temporary file."""
        try:
            # Don't save file objects, only metadata
            safe_data = {
                'timestamp': datetime.now().isoformat(),
                'step': data.get('merger_step'),
                'file_info': [
                    {
                        'name': info['name'],
                        'validation': info['validation']
                    } for info in (data.get('merger_info', []) or [])
                ] if data.get('merger_info') else None,
                'mappings': data.get('column_mappings'),
            }
            
            with open(StateManager.SAVE_FILE, 'w') as f:
                json.dump(safe_data, f)
                
        except Exception as e:
            st.error(f"Failed to save state: {str(e)}")
    
    @staticmethod
    def load_state() -> Optional[Dict[str, Any]]:
        """Load previously saved state if it exists."""
        try:
            if os.path.exists(StateManager.SAVE_FILE):
                with open(StateManager.SAVE_FILE, 'r') as f:
                    data = json.load(f)
                    
                # Verify state is recent (less than 1 hour old)
                saved_time = datetime.fromisoformat(data['timestamp'])
                age = (datetime.now() - saved_time).total_seconds() / 3600
                
                if age > 1:  # State is too old
                    os.remove(StateManager.SAVE_FILE)
                    return None
                    
                return data
                    
        except Exception as e:
            st.error(f"Failed to load saved state: {str(e)}")
            if os.path.exists(StateManager.SAVE_FILE):
                os.remove(StateManager.SAVE_FILE)
                
        return None
    
    @staticmethod
    def clear_state() -> None:
        """Clear saved state file."""
        try:
            if os.path.exists(StateManager.SAVE_FILE):
                os.remove(StateManager.SAVE_FILE)
        except Exception:
            pass