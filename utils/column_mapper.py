"""
Column Mapper Module
Handles intelligent column mapping between source and target schemas.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
try:
    from Levenshtein import ratio
    LEVENSHTEIN_AVAILABLE = True
except ImportError:
    LEVENSHTEIN_AVAILABLE = False
    # Fallback function for when Levenshtein is not available
    def ratio(s1, s2):
        """Fallback ratio function using difflib."""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, s1, s2).ratio()

class ColumnMapper:
    """Maps columns between source and target schemas using intelligent matching."""
    
    def __init__(self):
        # Import standard fields from SchemaAnalyzer
        from .schema_analyzer import SchemaAnalyzer
        self.standard_fields = SchemaAnalyzer.STANDARD_FIELDS
        self.target_schema = {field: {'type': 'text', 'required': True} for field in self.standard_fields}
        # Simple in-memory mapping history (replaced MappingHistory class)
        self.mapping_history = {}
    
    def show_mapping_interface(self, df: pd.DataFrame) -> tuple[Dict[str, str], bool]:
        """
        Display the column mapping interface in Streamlit with dropdown selection.
        
        Args:
            df: Input dataframe
            
        Returns:
            Tuple containing:
                - Dict mapping source columns to target columns
                - Boolean indicating if mappings should be applied
        """
        st.write("### Column Mapping")
        st.write("Map your source columns to the standard fields")
        
        # Initialize session state for mappings if not exists
        if 'column_mappings' not in st.session_state:
            st.session_state.column_mappings = {}
        
        # Get suggested mappings from history first, then fallback to automatic suggestions
        source_columns = list(df.columns)
        historical_mappings = self._get_suggested_mappings(source_columns)
        suggested_mappings = historical_mappings or self._suggest_column_mappings(source_columns)
        
        # Show found mapping if available
        if historical_mappings:
            st.success("🔍 Previous mapping found!")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("Suggested mappings from history:")
                for target, source in historical_mappings.items():
                    st.write(f"- {target} ← {source}")
            with col2:
                if st.button("Use This Mapping"):
                    # Apply the mappings and force a rerun to update UI
                    st.session_state.column_mappings = historical_mappings.copy()
                    st.success("Previous mapping applied!")
                    st.rerun()  # Force refresh to update all dropdowns
        
        # Show history button
        if st.button("📚 View Mapping History"):
            st.write("#### Previous Mappings")
            self._show_history_interface()
        
        # Add search/filter functionality
        search_term = st.text_input("🔍 Search fields", "")
        
        # Initialize custom fields in session state if not exists
        if 'custom_fields' not in st.session_state:
            st.session_state.custom_fields = set()

        # Create two columns for the interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write("#### Standard Fields")
            
            # Filter standard fields based on search term
            filtered_fields = [
                field for field in self.standard_fields 
                if search_term.lower() in field.lower()
            ]
            
            # Add a section for custom fields
            st.write("#### Custom Fields")
            col_a, col_b = st.columns([2, 3])
            with col_a:
                new_field = st.text_input("Add new field", key="new_field_input")
            with col_b:
                if st.button("Add Field", key="add_field_button"):
                    if new_field and new_field not in self.standard_fields:
                        st.session_state.custom_fields.add(new_field)
                        st.session_state.column_mappings[new_field] = ""
            
            # Show all custom fields with mapping dropdowns
            custom_fields = [
                field for field in st.session_state.custom_fields 
                if search_term.lower() in field.lower()
            ]
            
            # Create mapping interface for standard fields
            for target_col in filtered_fields:
                # Get current mapping or suggestion
                current_value = st.session_state.column_mappings.get(
                    target_col,
                    suggested_mappings.get(target_col, "")
                )
                
                # Create a row with label and dropdown
                col_a, col_b, col_c = st.columns([2, 3, 0.5])
                with col_a:
                    st.write(f"**{target_col}**")
                with col_b:
                    # Create options list excluding already mapped columns
                    mapped_columns = set(st.session_state.column_mappings.values())
                    available_columns = [""] + [
                        col for col in df.columns 
                        if col not in mapped_columns or col == current_value
                    ]
                    try:
                        index = available_columns.index(current_value) if current_value else 0
                    except ValueError:
                        index = 0
                        if current_value:  # If there was a mapping but column no longer exists
                            st.session_state.column_mappings.pop(target_col, None)
                    
                    selected = st.selectbox(
                        "Select source column",
                        options=available_columns,
                        index=index,
                        key=f"map_{target_col}",
                        label_visibility="collapsed"
                    )
                    if selected:
                        st.session_state.column_mappings[target_col] = selected
                    elif not selected:
                        # Safely remove the mapping if it exists
                        st.session_state.column_mappings.pop(target_col, None)
                        
            # Show all custom fields with mapping dropdowns
            if custom_fields:
                st.write("#### Custom Fields")
                for target_col in custom_fields:
                    current_value = st.session_state.column_mappings.get(target_col, "")
                    
                    # Create a row with label, dropdown, and delete button
                    col_a, col_b, col_c = st.columns([2, 3, 0.5])
                    with col_a:
                        st.write(f"**{target_col}**")
                    with col_b:
                        # Create options list excluding already mapped columns
                        mapped_columns = set(st.session_state.column_mappings.values())
                        available_columns = [""] + [
                            col for col in df.columns 
                            if col not in mapped_columns or col == current_value
                        ]
                        try:
                            index = available_columns.index(current_value) if current_value else 0
                        except ValueError:
                            index = 0
                            if current_value:  # If there was a mapping but column no longer exists
                                del st.session_state.column_mappings[target_col]
                        
                        selected = st.selectbox(
                            "Select source column",
                            options=available_columns,
                            index=index,
                            key=f"map_custom_{target_col}",
                            label_visibility="collapsed"
                        )
                        if selected:
                            st.session_state.column_mappings[target_col] = selected
                        elif target_col in st.session_state.column_mappings and not selected:
                            del st.session_state.column_mappings[target_col]
                    with col_c:
                        if st.button("🗑️", key=f"delete_{target_col}", help=f"Delete {target_col}"):
                            st.session_state.custom_fields.discard(target_col)  # Safely remove from set
                            st.session_state.column_mappings.pop(target_col, None)  # Safely remove mapping
        
        with col2:
            st.write("#### Quick Actions")
            # Add auto-map button
            if st.button("🎯 Auto-Map All"):
                # Clear existing mappings first
                st.session_state.column_mappings = {}
                # Apply new mappings
                st.session_state.column_mappings.update(suggested_mappings)
                st.success("Auto-mapping applied!")
                st.rerun()  # Force refresh to update all dropdowns
            
            # Add clear button
            if st.button("🗑️ Clear All"):
                st.session_state.column_mappings = {}
            
            # Show mapping stats
            st.write("---")
            st.write(f"**Mapped:** {len(st.session_state.column_mappings)}/{len(self.standard_fields)}")
            
            # Add apply button
            if st.button("✅ Apply Mappings", type="primary"):
                # Save mappings to history when applied
                if st.session_state.column_mappings:
                    self._save_mapping(
                        source_columns=list(df.columns),
                        mappings=st.session_state.column_mappings
                    )
                    st.success("Mappings saved to history!")
                return st.session_state.column_mappings, True
                
        return st.session_state.column_mappings, False
    
    def _show_mapping_preview(self, df: pd.DataFrame, mappings: Dict[str, str]) -> None:
        """
        Show a preview of the mapped data.
        
        Args:
            df: Input dataframe
            mappings: Dictionary of column mappings
        """
        if not mappings:
            return
            
        # Create a preview of the mapped data
        preview_data = {}
        for target_col, source_col in mappings.items():
            if source_col in df.columns:
                preview_data[target_col] = df[source_col]
        
        preview_df = pd.DataFrame(preview_data)
        st.write("First 5 rows of mapped data:")
        from .helpers import prepare_df_for_display
        st.dataframe(prepare_df_for_display(preview_df.head()), use_container_width=True)
        
        # Show mapping summary
        st.write("### Mapping Summary")
        mapped_cols = len(mappings)
        total_cols = len(self.standard_fields)
        st.write(f"Mapped {mapped_cols} out of {total_cols} columns")
        
        # Show unmapped standard fields
        unmapped = set(self.standard_fields) - set(mappings.keys())
        if unmapped:
            st.warning("Unmapped standard fields:")
            st.write(", ".join(sorted(unmapped)))
    
    def _suggest_column_mappings(self, source_columns: List[str]) -> Dict[str, str]:
        """
        Suggest column mappings based on name similarity.
        
        Args:
            source_columns: List of source column names
            
        Returns:
            Dict of suggested mappings
        """
        suggestions = {}
        for target_col in self.standard_fields:
            # Convert both column names to lowercase and remove special characters for comparison
            clean_target = ''.join(e.lower() for e in target_col if e.isalnum())
            best_match = None
            best_score = 0
            
            for source_col in source_columns:
                clean_source = ''.join(e.lower() for e in source_col if e.isalnum())
                score = ratio(clean_target, clean_source)
                if score > 0.8 and score > best_score:  # 0.8 is the similarity threshold
                    best_match = source_col
                    best_score = score
            
            if best_match:
                suggestions[target_col] = best_match
        
        return suggestions
        used_sources = set()
        
        for target_col in self.target_schema.keys():
            best_match = None
            best_score = 0
            
            for source_col in source_columns:
                if source_col in used_sources:
                    continue
                    
                # Calculate similarity score
                score = self._calculate_similarity(source_col, target_col)
                
                if score > best_score and score > 0.6:  # Threshold for suggestions
                    best_score = score
                    best_match = source_col
            
            if best_match:
                suggestions[target_col] = best_match
                used_sources.add(best_match)
        
        return suggestions
    
    def _calculate_similarity(self, source: str, target: str) -> float:
        """
        Calculate similarity between column names.
        
        Args:
            source: Source column name
            target: Target column name
            
        Returns:
            float: Similarity score between 0 and 1
        """
        # Clean and normalize names
        source = source.lower().replace('_', ' ')
        target = target.lower().replace('_', ' ')
        
        # Use Levenshtein distance for string similarity
        return ratio(source, target)
    
    
    def apply_mappings(self, df: pd.DataFrame, mappings: Dict[str, str]) -> pd.DataFrame:
        """
        Apply the column mappings to the dataframe.
        
        Args:
            df: Input dataframe
            mappings: Dictionary mapping target columns to source columns
            
        Returns:
            DataFrame with renamed and reordered columns according to mappings
        """
        if not mappings:
            return df
            
        # Create a new dataframe with mapped columns
        mapped_df = pd.DataFrame()
        
        # Add mapped standard fields first in their defined order
        for target_col in self.standard_fields:
            if target_col in mappings and mappings[target_col] in df.columns:
                mapped_df[target_col] = df[mappings[target_col]]
        
        # Add mapped custom fields
        if hasattr(st.session_state, 'custom_fields'):
            for target_col in st.session_state.custom_fields:
                if target_col in mappings and mappings[target_col] in df.columns:
                    mapped_df[target_col] = df[mappings[target_col]]
                
        # Add any unmapped columns at the end
        mapped_source_cols = set(mappings.values())
        unmapped_cols = [col for col in df.columns if col not in mapped_source_cols]
        for col in unmapped_cols:
            mapped_df[col] = df[col]
            
        return mapped_df
    
    def _get_suggested_mappings(self, source_columns: List[str]) -> Optional[Dict[str, str]]:
        """Get suggested mappings from history based on source columns."""
        # Simple implementation - look for exact column name matches
        suggestions = {}
        for source_col in source_columns:
            if source_col in self.mapping_history:
                suggestions[source_col] = self.mapping_history[source_col]
        return suggestions if suggestions else None
    
    def _show_history_interface(self):
        """Show mapping history interface."""
        if not self.mapping_history:
            st.info("No mapping history available.")
            return
        
        st.write("**Recent Mappings:**")
        for source_col, target_col in self.mapping_history.items():
            st.write(f"- {source_col} → {target_col}")
    
    def _save_mapping(self, source_columns: List[str], mappings: Dict[str, str]):
        """Save mapping to history."""
        for source_col, target_col in mappings.items():
            if source_col in source_columns:
                self.mapping_history[source_col] = target_col
