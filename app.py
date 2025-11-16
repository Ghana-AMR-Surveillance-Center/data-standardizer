"""
GLASS Data Standardizer v2.0.0
Main Streamlit application module for data standardization and AMR analysis.

This module provides a comprehensive web interface for:
- Single file data standardization
- Multiple file merging and processing
- Antimicrobial resistance (AMR) analysis
- Data validation and quality assessment
- Export functionality

Author: GLASS Data Standardizer Team
Version: 2.0.0
"""

import streamlit as st
import pandas as pd
from utils.file_handler import FileHandler
from utils.schema_analyzer import SchemaAnalyzer
from utils.column_mapper import ColumnMapper
from utils.transformer import DataTransformer
from utils.validator import DataValidator
from utils.excel_exporter import ExcelExporter
from utils.file_merger import FileMerger
from utils.data_quality import DataQualityAssessor
from utils.data_profiler import DataProfiler
from utils.logger import log_streamlit_action
from utils.user_feedback import user_feedback
from utils.cache_manager import clear_all_caches

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
    
    st.session_state['initialized'] = True

# Initialize components
try:
    file_handler = FileHandler()
    schema_analyzer = SchemaAnalyzer()
    column_mapper = ColumnMapper()
    transformer = DataTransformer()
    validator = DataValidator()
    excel_exporter = ExcelExporter()
    file_merger = FileMerger()
    quality_assessor = DataQualityAssessor()
    data_profiler = DataProfiler()
except Exception as e:
    st.error(f"❌ Failed to initialize application components: {str(e)}")
    st.error("Please check your installation and try again.")
    st.stop()

def main():
    """
    Main application function that orchestrates the GLASS Data Standardizer workflow.
    
    This function provides a comprehensive data standardization platform with:
    - Single file processing workflow
    - Multiple file merging capabilities
    - Advanced AMR analytics with statistical validation
    - Real-time data validation and quality assessment
    - Professional export functionality
    
    The application supports two main workflows:
    1. Single File: Upload → Map → Transform → Validate → Export
    2. Multiple Files: Upload → Merge → Transform → Validate → Export
    
    Features:
    - Intelligent column mapping with fuzzy matching
    - Data type detection and conversion
    - Statistical analysis with confidence intervals
    - Professional visualizations and reports
    - Comprehensive error handling and logging
    - Production-ready security and monitoring
    
    Returns:
        None
        
    Raises:
        Exception: If critical application components fail to initialize
    """
    
    # Main title
    st.title("🧬 GLASS Data Standardizer v2.0.0")
    st.markdown("---")
    
    # Sidebar navigation
    with st.sidebar:
        st.title("📋 Navigation")
        
        # Workflow selection
        if not st.session_state['workflow_selected']:
            st.markdown("### Select Workflow")
            workflow_type = st.radio(
                "Choose your workflow:",
                ["Single File", "Multiple Files"],
                help="Select whether you want to process a single file or merge multiple files"
            )
            
            if st.button("Start Workflow", type="primary"):
                st.session_state['workflow_type'] = 'single' if workflow_type == "Single File" else 'multiple'
                st.session_state['workflow_selected'] = True
                st.rerun()
        
        # Show current workflow
        if st.session_state['workflow_selected']:
            workflow_name = "Single File" if st.session_state['workflow_type'] == 'single' else "Multiple Files"
            st.success(f"✅ Active: {workflow_name}")
            
            if st.button("🔄 Start New Process"):
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
                
                clear_all_caches()
                st.rerun()
        
        # Cache management
        st.markdown("---")
        if st.button("🗑️ Clear Cache"):
            clear_all_caches()
            user_feedback.show_success("Cache cleared successfully!")
            st.rerun()
    
    # Main workflow logic
    if not st.session_state['workflow_selected']:
        # Show welcome screen
        st.markdown("""
        ## Welcome to GLASS Data Standardizer
        
        This application helps you standardize and process antimicrobial resistance (AMR) data.
        
        ### Features:
        - 📤 **Single File Processing**: Upload, map, transform, and validate a single data file
        - 📚 **Multiple File Merging**: Merge multiple files with intelligent column mapping
        - 🔍 **Data Validation**: Comprehensive data quality checks
        - 📊 **Data Profiling**: Statistical analysis and visualization
        - 📥 **Export**: Export standardized data in various formats
        
        ### Getting Started:
        1. Select your workflow type from the sidebar
        2. Follow the step-by-step process
        3. Export your standardized data
        
        ---
        """)
        
        # Show tips
        tips = [
            "Ensure your data files are in CSV or Excel format",
            "Column names will be automatically matched where possible",
            "You can manually adjust column mappings if needed",
            "All transformations are reversible until you export"
        ]
        user_feedback.show_tips(tips, "💡 Getting Started Tips")
        
        return
    
    # Single File Workflow
    if st.session_state['workflow_type'] == 'single':
        try:
            # Step 1: Upload
            if not st.session_state['single_steps']['upload']:
                st.markdown('<h2 class="step-header">Step 1: Upload Data</h2>', unsafe_allow_html=True)
                
                uploaded_df = file_handler.upload_file()
                
                if uploaded_df is not None:
                    st.session_state['data'] = uploaded_df
                    st.session_state['single_steps']['upload'] = True
                    user_feedback.show_success(f"Successfully uploaded {len(uploaded_df)} rows with {len(uploaded_df.columns)} columns")
                    log_streamlit_action("file_upload", f"Single file workflow - {len(uploaded_df)} rows, {len(uploaded_df.columns)} columns")
                    user_feedback.show_data_summary(uploaded_df, "Uploaded Data Summary")
                    st.rerun()
            
            # Step 2: Column Mapping
            if st.session_state['single_steps']['upload'] and not st.session_state['single_steps']['mapping']:
                st.markdown('<h2 class="step-header">Step 2: Column Mapping</h2>', unsafe_allow_html=True)
                
                mappings, confirmed = column_mapper.show_mapping_interface(st.session_state['data'])
                
                if confirmed:
                    st.session_state['mapped_columns'] = mappings
                    st.session_state['single_steps']['mapping'] = True
                    st.session_state['data'] = column_mapper.apply_mappings(st.session_state['data'], mappings)
                    user_feedback.show_success("Column mapping completed successfully!")
                    log_streamlit_action("column_mapping", f"Mapped {len(mappings)} columns")
                    st.rerun()
            
            # Step 3: Data Transformation
            if st.session_state['single_steps']['mapping'] and not st.session_state['single_steps']['transform']:
                st.markdown('<h2 class="step-header">Step 3: Data Transformation</h2>', unsafe_allow_html=True)
                
                transformed_df = transformer.show_transformation_interface(st.session_state['data'])
                
                if transformed_df is not None:
                    st.session_state['data'] = transformed_df
                    st.session_state['single_steps']['transform'] = True
                    user_feedback.show_success("Data transformation completed successfully!")
                    log_streamlit_action("data_transformation", "Applied transformations")
                    st.rerun()
            
            # Step 4: Validation and Export
            if st.session_state['single_steps']['transform']:
                st.markdown('<h2 class="step-header">Step 4: Validate and Export</h2>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Run Validation", use_container_width=True):
                        validation_results = validator.validate_data(st.session_state['data'])
                        st.session_state['validation_results'] = validation_results
                        st.session_state['single_steps']['validate'] = True
                        
                        with st.expander("Validation Results", expanded=True):
                            st.json(validation_results)
                
                with col2:
                    if st.button("Export Data", use_container_width=True, type="primary"):
                        excel_exporter.export_data(st.session_state['data'])
                        user_feedback.show_success("Data exported successfully!")
                        log_streamlit_action("data_export", "Exported standardized data")
        
        except Exception as e:
            st.error(f"❌ Error in single file workflow: {str(e)}")
            st.error("Please try again or contact support if the issue persists.")
            log_streamlit_action("error", f"Single file workflow error: {str(e)}")
    
    # Multiple Files Workflow
    elif st.session_state['workflow_type'] == 'multiple':
        try:
            # Upload and Merge
            if not st.session_state['multiple_steps']['upload']:
                st.markdown('<h2 class="step-header">Step 1: Upload and Merge Files</h2>', unsafe_allow_html=True)
                
                merged_df = file_merger.show_merger_interface()
                
                if merged_df is not None:
                    st.session_state['data'] = merged_df
                    st.session_state['multiple_steps']['upload'] = True
                    st.session_state['multiple_steps']['merge'] = True
                    user_feedback.show_success(f"Successfully merged files: {len(merged_df)} rows, {len(merged_df.columns)} columns")
                    log_streamlit_action("file_merge", f"Multiple files - {len(merged_df)} rows, {len(merged_df.columns)} columns")
                    st.rerun()
            
            # Transform (Multiple Files)
            if st.session_state['multiple_steps']['merge'] and not st.session_state['multiple_steps']['transform']:
                st.markdown('<h2 class="step-header">Step 2: Data Transformation</h2>', unsafe_allow_html=True)
                
                transformed_df = transformer.show_transformation_interface(st.session_state['data'])
                
                if transformed_df is not None:
                    st.session_state['data'] = transformed_df
                    st.session_state['multiple_steps']['transform'] = True
                    user_feedback.show_success("Data transformation completed successfully!")
                    log_streamlit_action("data_transformation", "Applied transformations")
                    st.rerun()
            
            # Validation and Export (Multiple Files)
            if st.session_state['multiple_steps']['transform']:
                st.markdown('<h2 class="step-header">Step 3: Validate and Export</h2>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Run Validation", use_container_width=True):
                        validation_results = validator.validate_data(st.session_state['data'])
                        st.session_state['validation_results'] = validation_results
                        st.session_state['multiple_steps']['validate'] = True
                        
                        with st.expander("Validation Results", expanded=True):
                            st.json(validation_results)
                
                with col2:
                    if st.button("Export Data", use_container_width=True, type="primary"):
                        excel_exporter.export_data(st.session_state['data'])
                        user_feedback.show_success("Data exported successfully!")
                        log_streamlit_action("data_export", "Exported standardized data")

        except Exception as e:
            st.error(f"❌ Error in multiple files workflow: {str(e)}")
            st.error("Please try again or contact support if the issue persists.")
            log_streamlit_action("error", f"Multiple files workflow error: {str(e)}")

if __name__ == "__main__":
    main()




