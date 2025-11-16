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
from utils.data_quality import DataQualityAssessor
from utils.data_profiler import DataProfiler
from utils.logger import log_streamlit_action
from utils.config import get_config

# Configure Streamlit page
st.set_page_config(
    page_title="GLASS Data Standardizer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'initialized' not in st.session_state:
    # Data states
    st.session_state['data'] = None
    st.session_state['mapped_columns'] = {}
    st.session_state['validation_results'] = None
    st.session_state['workflow_selected'] = False
    st.session_state['workflow_type'] = None  # 'single' or 'multiple'
    
    # Progress tracking for single file workflow
    st.session_state['single_steps'] = {
        'upload': False,
        'mapping': False,
        'transform': False,
        'validate': False
    }
    
    # Progress tracking for multiple files workflow
    st.session_state['multiple_steps'] = {
        'upload': False,
        'merge': False,
        'transform': False,
        'validate': False
    }
    
    # Clear any legacy session state
    keys_to_remove = [key for key in st.session_state.keys() if isinstance(key, str) and 'mapping_' in key]
    for key in keys_to_remove:
        del st.session_state[key]
    
    st.session_state['initialized'] = True

# Custom styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
    }
    .step-header {
        font-size: 1.8rem;
        font-weight: 600;
        margin: 1.5rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #cce5ff;
        border: 1px solid #b8daff;
        color: #004085;
    }
    </style>
    """, unsafe_allow_html=True)

def show_progress():
    """Display the progress bar and completion status based on workflow type."""
    if not st.session_state['workflow_selected']:
        return
    
    if st.session_state['workflow_type'] == 'single':
        steps = st.session_state['single_steps']
        col1, col2, col3, col4 = st.columns(4)
        progress = sum(steps.values()) / len(steps)
        
        st.progress(progress)
        with col1:
            st.write("📤 Upload" + (" ✅" if steps['upload'] else ""))
        with col2:
            st.write("🔗 Map" + (" ✅" if steps['mapping'] else "") + " (Optional)")
        with col3:
            st.write("🔧 Transform" + (" ✅" if steps['transform'] else ""))
        with col4:
            st.write("✔️ Validate" + (" ✅" if steps['validate'] else ""))
    
    else:  # multiple files workflow
        steps = st.session_state['multiple_steps']
        col1, col2, col3, col4 = st.columns(4)
        progress = sum(steps.values()) / len(steps)
        
        st.progress(progress)
        with col1:
            st.write("📤 Upload" + (" ✅" if steps['upload'] else ""))
        with col2:
            st.write("🔄 Merge" + (" ✅" if steps['merge'] else ""))
        with col3:
            st.write("🔧 Transform" + (" ✅" if steps['transform'] else ""))
        with col4:
            st.write("✔️ Validate" + (" ✅" if steps['validate'] else ""))

def main():
    # Initialize components
    config = get_config()
    file_handler = FileHandler()
    schema_analyzer = SchemaAnalyzer()
    column_mapper = ColumnMapper()
    transformer = DataTransformer()
    validator = DataValidator()
    excel_exporter = ExcelExporter()
    file_merger = FileMerger()
    quality_assessor = DataQualityAssessor()
    data_profiler = DataProfiler()
    
    # Sidebar with logo and essential info
    with st.sidebar:
        st.image("https://www.auruminstitute.org/images/logo-header.png", width=200)
        st.markdown("## GLASS Data Standardizer")
        
        st.markdown("---")
        st.markdown("### Quick Guide")
        
        # Update quick guide based on workflow
        if not st.session_state['workflow_selected']:
            st.info("Choose your workflow to begin")
        elif st.session_state['workflow_type'] == 'single':
            st.info("""
            1. Upload your data file
            2. Map columns (optional)
            3. Transform data values
            4. Validate and export
            """)
        else:
            st.info("""
            1. Upload your data files
            2. Merge files (includes mapping)
            3. Transform data values
            4. Validate and export
            """)
        
        st.markdown("---")
        st.caption("Version 1.0.0 | © 2025 The Aurum Institute")
        st.caption("[Need help?](mailto:support@auruminstitute.org)")
    
    # Main content
    st.markdown('<h1 class="main-header">GLASS Data Standardizer</h1>', unsafe_allow_html=True)
    
    # Workflow Selection
    if not st.session_state['workflow_selected']:
        st.markdown('<h2 class="step-header">Choose Your Workflow</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Standardize Single File", use_container_width=True):
                st.session_state['workflow_type'] = 'single'
                st.session_state['workflow_selected'] = True
                st.rerun()
        
        with col2:
            if st.button("📚 Merge Multiple Files", use_container_width=True):
                st.session_state['workflow_type'] = 'multiple'
                st.session_state['workflow_selected'] = True
                st.rerun()
        
        st.markdown("---")
        st.info("ℹ️ Choose 'Standardize Single File' if you have one file to process, or 'Merge Multiple Files' if you need to combine and standardize multiple files.")
        return
    
    # Show progress based on selected workflow
    show_progress()
    
    # Single File Workflow
    if st.session_state['workflow_type'] == 'single':
        # Upload
        if not st.session_state['single_steps']['upload']:
            st.markdown('<h2 class="step-header">Step 1: Upload Your Data</h2>', unsafe_allow_html=True)
            uploaded_df = file_handler.upload_file()
            
            if uploaded_df is not None:
                st.session_state['data'] = uploaded_df
                st.session_state['single_steps']['upload'] = True
                log_streamlit_action("file_upload", f"Single file workflow - {len(uploaded_df)} rows, {len(uploaded_df.columns)} columns")
                
                with st.expander("View Data Preview", expanded=True):
                    file_handler.preview_data(uploaded_df)
                    schema_info = schema_analyzer.analyze_schema(uploaded_df)
                    st.write("### Column Information")
                    st.json(schema_info)
                
                # Add data quality assessment
                with st.expander("📊 Data Quality Assessment", expanded=False):
                    quality_results = quality_assessor.assess_data_quality(uploaded_df)
                    quality_assessor.show_quality_report(quality_results)
                
                # Add data profiling
                with st.expander("🔍 Data Profile", expanded=False):
                    profile_results = data_profiler.profile_dataframe(uploaded_df)
                    data_profiler.show_profile_report(profile_results)
        
        # Optional Mapping
        if st.session_state['single_steps']['upload'] and not st.session_state['single_steps']['mapping']:
            st.markdown('<h2 class="step-header">Step 2: Column Mapping (Optional)</h2>', unsafe_allow_html=True)
            
            # Show current column names
            st.write("### Current Column Names")
            cols_df = pd.DataFrame({'Column Name': st.session_state['data'].columns})
            st.dataframe(cols_df, use_container_width=True)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                needs_mapping = st.radio(
                    "Do you need to map these columns to standard names?",
                    ["Yes", "No, skip mapping"],
                    horizontal=True
                )
            
            if needs_mapping == "Yes":
                mappings, should_apply = column_mapper.show_mapping_interface(st.session_state['data'])
                if should_apply and mappings:
                    st.session_state['data'] = column_mapper.apply_mappings(st.session_state['data'], mappings)
                    st.session_state['mapped_columns'] = mappings
                    st.session_state['single_steps']['mapping'] = True
            else:
                st.session_state['single_steps']['mapping'] = True
        
        # Transform (Single File)
        if st.session_state['single_steps']['mapping'] and not st.session_state['single_steps']['transform']:
            st.markdown('<h2 class="step-header">Step 3: Transform Data</h2>', unsafe_allow_html=True)
            transformed_df = transformer.show_transformation_interface(
                st.session_state['data']
            )
            
            if transformed_df is not None:
                st.session_state['data'] = transformed_df
                st.session_state['single_steps']['transform'] = True
    
    # Multiple Files Workflow
    else:
        # Upload and Merge
        if not st.session_state['multiple_steps']['upload']:
            st.markdown('<h2 class="step-header">Step 1: Upload and Merge Files</h2>', unsafe_allow_html=True)
            merged_df = file_merger.show_merger_interface()
            
            if merged_df is not None:
                st.session_state['data'] = merged_df
                st.session_state['multiple_steps']['upload'] = True
                st.session_state['multiple_steps']['merge'] = True
        
        # Transform (Multiple Files)
        if st.session_state['multiple_steps']['merge'] and not st.session_state['multiple_steps']['transform']:
            st.markdown('<h2 class="step-header">Step 2: Transform Data</h2>', unsafe_allow_html=True)
            transformed_df = transformer.show_transformation_interface(
                st.session_state['data']
            )
            
            if transformed_df is not None:
                st.session_state['data'] = transformed_df
                st.session_state['multiple_steps']['transform'] = True
    
    # Validation and Export (Common for both workflows)
    steps = st.session_state['single_steps'] if st.session_state['workflow_type'] == 'single' else st.session_state['multiple_steps']
    
    if steps['transform']:
        st.markdown('<h2 class="step-header">Final Step: Validate and Export</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Run Validation", use_container_width=True):
                validation_results = validator.validate_data(
                    st.session_state['data']
                )
                st.session_state['validation_results'] = validation_results
                steps['validate'] = True
                
                with st.expander("Validation Results", expanded=True):
                    validator.show_validation_results(validation_results)
        
        with col2:
            if st.button("Export Data", use_container_width=True, type="primary"):
                excel_exporter.show_export_interface(
                    st.session_state['data'],
                    st.session_state.get('validation_results')
                )
    
    # Reset workflow button
    if st.session_state['workflow_selected']:
        st.markdown("---")
        if st.button("Start New Process", type="secondary"):
            # Reset all state
            st.session_state['workflow_selected'] = False
            st.session_state['workflow_type'] = None
            st.session_state['data'] = None
            st.session_state['mapped_columns'] = {}
            st.session_state['validation_results'] = None
            
            # Reset progress tracking
            for key in st.session_state['single_steps']:
                st.session_state['single_steps'][key] = False
            for key in st.session_state['multiple_steps']:
                st.session_state['multiple_steps'][key] = False
                
            st.rerun()

if __name__ == "__main__":
    main()

