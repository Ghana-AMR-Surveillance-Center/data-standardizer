"""
Mapping History Module
Manages saving and loading of column mapping history.
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path
import streamlit as st

class MappingHistory:
    """Manages column mapping history."""
    
    def __init__(self):
        self.history_file = Path("mapping_history.json")
        self._load_history()
    
    def _load_history(self) -> None:
        """Load mapping history from file."""
        if not hasattr(st.session_state, 'mapping_history'):
            st.session_state.mapping_history = {}
            
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    st.session_state.mapping_history = json.load(f)
            except json.JSONDecodeError:
                st.session_state.mapping_history = {}
    
    def save_mapping(self, source_columns: List[str], mappings: Dict[str, str]) -> None:
        """
        Save a new mapping to history.
        
        Args:
            source_columns: List of original column names
            mappings: Dictionary of target to source column mappings
        """
        # Create a key based on source columns
        source_key = '|'.join(sorted(source_columns))
        
        # Update history
        if source_key not in st.session_state.mapping_history:
            st.session_state.mapping_history[source_key] = []
        
        # Add new mapping if it doesn't exist
        mapping_entry = {
            'source_columns': source_columns,
            'mappings': mappings
        }
        
        if mapping_entry not in st.session_state.mapping_history[source_key]:
            st.session_state.mapping_history[source_key].append(mapping_entry)
        
        # Save to file
        with open(self.history_file, 'w') as f:
            json.dump(st.session_state.mapping_history, f, indent=2)
    
    def get_suggested_mappings(self, source_columns: List[str]) -> Optional[Dict[str, str]]:
        """
        Get suggested mappings based on source columns.
        
        Args:
            source_columns: List of column names to find mappings for
            
        Returns:
            Dictionary of suggested mappings or None if no matches found
        """
        # Try exact match first
        source_key = '|'.join(sorted(source_columns))
        if source_key in st.session_state.mapping_history:
            # Return the most recent mapping
            return st.session_state.mapping_history[source_key][-1]['mappings']
        
        # Try partial matches
        best_match = None
        best_match_score = 0
        
        for history_key, history_entries in st.session_state.mapping_history.items():
            history_cols = set(history_entries[0]['source_columns'])
            current_cols = set(source_columns)
            
            # Calculate similarity score
            common_cols = len(history_cols.intersection(current_cols))
            total_cols = len(history_cols.union(current_cols))
            similarity = common_cols / total_cols if total_cols > 0 else 0
            
            if similarity > best_match_score and similarity > 0.5:  # At least 50% similar
                best_match_score = similarity
                best_match = history_entries[-1]['mappings']  # Use most recent mapping
        
        return best_match
    
    def show_history_interface(self) -> None:
        """Display the mapping history interface."""
        if not st.session_state.mapping_history:
            st.info("No mapping history available yet.")
            return
        
        st.write("#### Previous Mappings")
        
        # Create a table of mappings
        for source_key, history_entries in st.session_state.mapping_history.items():
            st.write(f"**Source Columns:** {', '.join(history_entries[0]['source_columns'])}")
            
            # Create columns for each mapping entry
            cols = st.columns(min(len(history_entries), 3))  # Show up to 3 mappings side by side
            
            for idx, (entry, col) in enumerate(zip(history_entries[-3:], cols)):  # Show last 3 mappings
                with col:
                    st.write(f"Mapping {len(history_entries) - 2 + idx}:")
                    for target, source in entry['mappings'].items():
                        st.write(f"- {target} ← {source}")
            
            st.write("---")
