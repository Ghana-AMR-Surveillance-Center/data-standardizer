import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Dict, Any
from utils.file_handler import FileHandler
from utils.schema_analyzer import SchemaAnalyzer
from utils.column_mapper import ColumnMapper
from utils.data_filter import DataFilter
from utils.transformer import DataTransformer
from utils.validator import DataValidator
from utils.excel_exporter import ExcelExporter
from utils.file_merger import FileMerger
from utils.helpers import generate_summary_stats

# Configure Streamlit page
st.set_page_config(
    page_title="GLASS Data Standardizer",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clear any cached widget keys that might cause conflicts
if 'widget_key_reset' not in st.session_state:
    # Remove any problematic keys from session state
    keys_to_remove = [key for key in st.session_state.keys() if isinstance(key, str) and 'mapping_' in key]
    for key in keys_to_remove:
        del st.session_state[key]
    st.session_state['widget_key_reset'] = True

# Initialize session state if needed
if 'data' not in st.session_state:
    st.session_state['data'] = None
if 'mapped_columns' not in st.session_state:
    st.session_state['mapped_columns'] = {}
if 'validation_results' not in st.session_state:
    st.session_state['validation_results'] = None

def main():
    # Header
    st.title("GLASS Data Standardizer")
    st.markdown("---")
    
    # Initialize components
    file_handler = FileHandler()
    schema_analyzer = SchemaAnalyzer()
    column_mapper = ColumnMapper()
    data_filter = DataFilter()
    transformer = DataTransformer()
    validator = DataValidator()
    excel_exporter = ExcelExporter()
    file_merger = FileMerger()
    
    # Sidebar with logo and info
    with st.sidebar:
        # Logo and title section
        st.image("https://www.auruminstitute.org/images/logo-header.png", width=200)
        st.title("GLASS Data Standardizer")
        
        # Navigation section
        st.markdown("---")
        st.subheader("Navigation")
        page = st.radio(
            "Go to",
            ["Upload Data", "Merge Files", "Map Columns", "Filter Data", "Transform Data", "Validate", "Export"]
        )
        
        # Project info
        st.markdown("---")
        st.markdown("""
        ### About
        GLASS Data Standardization Tool for AMR surveillance data processing and standardization.
        
        ### Institution
        The Aurum Institute NPC
        
        ### Version
        1.0.0
        """)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        ### Contact
        For support: [support@auruminstitute.org](mailto:support@auruminstitute.org)
        
        © 2025 The Aurum Institute
        """)
    
    # File Upload Page
    if page == "Upload Data":
        st.header("Upload Your Data")
        uploaded_df = file_handler.upload_file()
        
        if uploaded_df is not None:
            st.session_state['data'] = uploaded_df
            schema_info = schema_analyzer.analyze_schema(uploaded_df)
            st.write("### Schema Analysis")
            st.json(schema_info)
            file_handler.preview_data(uploaded_df)
    
    # File Merger Page
    elif page == "Merge Files":
        st.header("Merge Excel Files")
        merged_df = file_merger.show_merger_interface()
        if merged_df is not None:
            st.session_state['data'] = merged_df
            st.markdown("---")
            st.subheader("Export Merged Data")
            excel_exporter.show_export_interface(merged_df, None)
    
    # Column Mapping Page
    elif page == "Map Columns" and st.session_state['data'] is not None:
        st.header("Map Columns")
        mappings, should_apply = column_mapper.show_mapping_interface(
            st.session_state['data']
        )
        st.session_state['mapped_columns'] = mappings
        
        # Apply mappings if requested
        if should_apply and mappings:
            st.session_state['data'] = column_mapper.apply_mappings(
                st.session_state['data'], 
                mappings
            )
            st.success("✅ Mappings applied successfully!")
            st.write("### Preview of Mapped Data")
            st.dataframe(st.session_state['data'].head(), use_container_width=True)
            st.markdown("---")
            st.subheader("Export Mapped Data")
            excel_exporter.show_export_interface(st.session_state['data'], None)
    
    # Data Filtering Page
    elif page == "Filter Data" and st.session_state['data'] is not None:
        st.header("Filter Data")
        filtered_df = data_filter.show_filter_interface(
            st.session_state['data']
        )
        if filtered_df is not None:
            st.session_state['data'] = filtered_df
            st.markdown("---")
            st.subheader("Export Filtered Data")
            excel_exporter.show_export_interface(filtered_df, None)
    
    # Data Transformation Page
    elif page == "Transform Data" and st.session_state['data'] is not None:
        st.header("Transform Data")
        transformed_df = transformer.show_transformation_interface(
            st.session_state['data']
        )
        if transformed_df is not None:
            st.session_state['data'] = transformed_df
            st.markdown("---")
            st.subheader("Export Transformed Data")
            excel_exporter.show_export_interface(transformed_df, None)
    
    # Validation Page
    elif page == "Validate" and st.session_state['data'] is not None:
        st.header("Validate Data")
        validation_results = validator.validate_data(
            st.session_state['data']
        )
        st.session_state['validation_results'] = validation_results
        validator.show_validation_results(validation_results)
        st.markdown("---")
        st.subheader("Export Validated Data")
        excel_exporter.show_export_interface(
            st.session_state['data'],
            validation_results
        )
    
    # Export Page
    elif page == "Export" and st.session_state['data'] is not None:
        st.header("Export Data")
        excel_exporter.show_export_interface(
            st.session_state['data'],
            st.session_state.get('validation_results')
        )
    
    # No data loaded warning
    elif st.session_state['data'] is None and page != "Upload Data":
        st.warning("Please upload data first!")

if __name__ == "__main__":
    main()
