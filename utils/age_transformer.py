"""
Age Transformer Module
Handles age value standardization to years.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
from .helpers import preview_age_conversions, convert_age_column

class AgeTransformer:
    """Handles age value standardization."""
    
    def show_age_standardization_interface(
        self,
        df: pd.DataFrame,
        age_column: str
    ) -> pd.DataFrame:
        """
        Display interface for standardizing age values.
        
        Args:
            df: Input dataframe
            age_column: Name of the age column
            
        Returns:
            DataFrame with standardized ages
        """
        st.write("### Age Standardization")
        st.write("Review and approve age value conversions to years")
        
        # Initialize session state for approved conversions
        if 'approved_age_conversions' not in st.session_state:
            st.session_state.approved_age_conversions = {}
        
        # Get preview of conversions
        preview_df = preview_age_conversions(df, age_column)
        
        if preview_df.empty:
            st.warning(f"No age values found in column '{age_column}' that need conversion.")
            return df
        
        # Show preview with approval checkboxes
        st.write("#### Review Conversions")
        st.write("Select which conversions to apply:")
        st.write("The age values will be converted to numeric years. Original values will be preserved in a backup column.")
        
        for idx, row in preview_df.iterrows():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            with col1:
                st.write(f"Original: **{row['Original']}**")
            with col2:
                st.write(f"Converted: **{row['Converted (Years)']:.2f} years**")
            with col3:
                # Allow manual adjustment of converted value
                adjusted_value = st.number_input(
                    "Adjust value",
                    value=float(row['Converted (Years)']),
                    step=0.1,
                    format="%.2f",
                    key=f"adjust_age_{idx}",
                    label_visibility="collapsed"
                )
            with col4:
                key = f"approve_age_{idx}"
                if st.checkbox("Approve", key=key, value=True):
                    st.session_state.approved_age_conversions[str(row['Original'])] = adjusted_value
                else:
                    st.session_state.approved_age_conversions.pop(str(row['Original']), None)
        
        # Apply conversions button
        if st.button("Apply Selected Conversions"):
            if st.session_state.approved_age_conversions:
                df = convert_age_column(
                    df,
                    age_column,
                    st.session_state.approved_age_conversions
                )
                st.success("Age values have been standardized to years!")
            else:
                st.warning("No conversions were selected to apply.")
        
        return df
