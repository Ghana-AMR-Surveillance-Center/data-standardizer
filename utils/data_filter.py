"""
Data Filter Module
Provides filtering capabilities for dataframe columns.
"""

import streamlit as st
import pandas as pd
import re
from typing import Dict, List, Any, Optional

class DataFilter:
    """Handles data filtering operations."""
    
    def __init__(self):
        self.filter_types = {
            'text': ['equals', 'contains', 'starts_with', 'ends_with', 'regex'],
            'number': ['equals', 'greater_than', 'less_than', 'between'],
            'date': ['equals', 'after', 'before', 'between'],
            'boolean': ['equals']
        }
    
    def show_filter_interface(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Display the filtering interface in Streamlit.
        
        Args:
            df: Input dataframe
            
        Returns:
            Filtered dataframe
        """
        st.write("### Data Filtering")
        
        # Initialize filters in session state
        if 'filters' not in st.session_state:
            st.session_state['filters'] = []
        
        # Add filter button
        if st.button("Add Filter"):
            st.session_state['filters'].append({})
        
        # Filter interface
        filtered_df = df.copy()
        for i, filter_dict in enumerate(st.session_state['filters']):
            st.write(f"#### Filter {i + 1}")
            
            # Create columns for filter controls
            col1, col2, col3 = st.columns(3)
            
            with col1:
                column = st.selectbox(
                    "Column",
                    options=df.columns,
                    key=f"col_{i}"
                )
            
            with col2:
                filter_type = None
                if column:  # Only show filter type if column is selected
                    filter_type = st.selectbox(
                        "Filter Type",
                        options=self._get_filter_types(df[column].dtype),
                        key=f"type_{i}"
                    )
            
            with col3:
                filter_value = None
                if column and filter_type:  # Only show value input if both column and type are selected
                    filter_value = self._get_filter_value_input(
                        df[column],
                        filter_type,
                        i
                    )
            
            # Apply filter if all values are selected
            if column and filter_type and filter_value is not None:
                filtered_df = self._apply_filter(
                    filtered_df,
                    column,
                    filter_type,
                    filter_value
                )
            
            # Remove filter button
            if st.button("Remove Filter", key=f"remove_{i}"):
                st.session_state['filters'].pop(i)
                st.rerun()
        
        # Show filtering results
        st.write("### Filtered Data Preview")
        st.write(f"Showing {len(filtered_df)} of {len(df)} rows")
        from .helpers import prepare_df_for_display
        st.dataframe(prepare_df_for_display(filtered_df.head()), use_container_width=True)
        
        return filtered_df
    
    def _get_filter_types(self, dtype) -> List[str]:
        """
        Get appropriate filter types for a column's data type.
        
        Args:
            dtype: Column data type
            
        Returns:
            List of applicable filter types
        """
        if pd.api.types.is_numeric_dtype(dtype):
            return self.filter_types['number']
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return self.filter_types['date']
        elif pd.api.types.is_bool_dtype(dtype):
            return self.filter_types['boolean']
        else:
            return self.filter_types['text']
    
    def _get_filter_value_input(
        self,
        series: pd.Series,
        filter_type: str,
        index: int
    ) -> Any:
        """
        Create appropriate input widget based on filter type.
        
        Args:
            series: Column data
            filter_type: Type of filter
            index: Filter index for unique keys
            
        Returns:
            Filter value(s)
        """
        if filter_type == 'between':
            col1, col2 = st.columns(2)
            with col1:
                value1 = st.number_input(
                    "Min Value",
                    value=float(series.min()),
                    key=f"value1_{index}"
                )
            with col2:
                value2 = st.number_input(
                    "Max Value",
                    value=float(series.max()),
                    key=f"value2_{index}"
                )
            return (value1, value2)
        
        elif filter_type in ['equals', 'contains', 'starts_with', 'ends_with']:
            if pd.api.types.is_numeric_dtype(series.dtype):
                return st.number_input(
                    "Value",
                    value=float(series.mean()),
                    key=f"value_{index}"
                )
            else:
                return st.text_input(
                    "Value",
                    key=f"value_{index}"
                )
        
        elif filter_type == 'regex':
            return st.text_input(
                "Regular Expression",
                key=f"value_{index}"
            )
        
        else:  # greater_than, less_than
            return st.number_input(
                "Value",
                value=float(series.mean()),
                key=f"value_{index}"
            )
    
    def _apply_filter(
        self,
        df: pd.DataFrame,
        column: str,
        filter_type: str,
        filter_value: Any
    ) -> pd.DataFrame:
        """
        Apply filter to dataframe.
        
        Args:
            df: Input dataframe
            column: Column to filter
            filter_type: Type of filter
            filter_value: Filter value(s)
            
        Returns:
            Filtered dataframe
        """
        if filter_type == 'equals':
            return df[df[column] == filter_value]
            
        elif filter_type == 'contains':
            return df[df[column].astype(str).str.contains(
                str(filter_value),
                case=False,
                na=False
            )]
            
        elif filter_type == 'starts_with':
            return df[df[column].astype(str).str.startswith(
                str(filter_value),
                na=False
            )]
            
        elif filter_type == 'ends_with':
            return df[df[column].astype(str).str.endswith(
                str(filter_value),
                na=False
            )]
            
        elif filter_type == 'regex':
            try:
                return df[df[column].astype(str).str.match(
                    str(filter_value),
                    na=False
                )]
            except re.error:
                st.error("Invalid regular expression")
                return df
            
        elif filter_type == 'greater_than':
            return df[df[column] > filter_value]
            
        elif filter_type == 'less_than':
            return df[df[column] < filter_value]
            
        elif filter_type == 'between':
            value1, value2 = filter_value
            return df[(df[column] >= value1) & (df[column] <= value2)]
        
        return df
