"""
GLASS Data Standardizer v2.0.0
Main application module for data standardization and AMR analysis.

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
from utils.amr_interface import AMRInterface
from utils.enhanced_amr_interface import EnhancedAMRInterface
from utils.logger import log_streamlit_action
from utils.app_config import app_config
from utils.user_feedback import user_feedback
from utils.app_settings import app_settings
from utils.cache_manager import clear_all_caches
from utils.production_logger import initialize_production_logger, get_production_logger
from config.production import production_config

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
    
    # Progress tracking for AMR analytics workflow
    st.session_state['amr_steps'] = {
        'upload': False,
        'analyze': False
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
    
    elif st.session_state['workflow_type'] == 'multiple':
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
    
    else:  # AMR analytics workflow
        steps = st.session_state['amr_steps']
        col1, col2 = st.columns(2)
        progress = sum(steps.values()) / len(steps)
        
        st.progress(progress)
        with col1:
            st.write("📤 Upload Data" + (" ✅" if steps['upload'] else ""))
        with col2:
            st.write("🧬 AMR Analysis" + (" ✅" if steps['analyze'] else ""))

def main():
    """
    Main application function that orchestrates the GLASS Data Standardizer workflow.
    
    This function provides a comprehensive data standardization platform with:
    - Single file processing workflow
    - Multiple file merging capabilities
    - Advanced AMR analytics with statistical validation
    - Real-time data validation and quality assessment
    - Professional export functionality
    
    The application supports three main workflows:
    1. Single File: Upload → Map → Transform → Validate → Export
    2. Multiple Files: Upload → Merge → Transform → Validate → Export
    3. AMR Analytics: Upload → Analyze → Generate Reports → Export
    
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
    try:
        # Initialize production components
        if not production_config.validate_config():
            st.warning("⚠️ Using development configuration. Set environment variables for production.")
        
        # Initialize production logger (with error handling)
        logger = None
        try:
            logger = initialize_production_logger(production_config.get_logging_config())
            logger.log_application_start(production_config.version, production_config.environment)
        except Exception as e:
            st.warning(f"⚠️ Production logging not available: {str(e)}")
        
        # Initialize components with error handling
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
            return
        
        # Sidebar with logo and essential info
        with st.sidebar:
            st.image("https://www.auruminstitute.org/images/logo-header.png", width=200)
            st.markdown("## GLASS Data Standardizer")
            
            # Show settings UI
            app_settings.show_settings_ui()
            
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
            elif st.session_state['workflow_type'] == 'multiple':
                st.info("""
                1. Upload your data files
                2. Merge files (includes mapping)
                3. Transform data values
                4. Validate and export
                """)
            else:  # AMR analytics
                st.info("""
                1. Upload AMR data
                2. Review data detection
                3. Run analysis
                4. Export results
                """)
            
            # Show workflow guide
            if st.session_state['workflow_selected']:
                if st.session_state['workflow_type'] == 'single':
                    steps = [
                        {"title": "Upload Data", "description": "Select and upload your data file"},
                        {"title": "Map Columns", "description": "Configure column mappings (optional)"},
                        {"title": "Transform Data", "description": "Clean and standardize data"},
                        {"title": "Validate & Export", "description": "Verify quality and download results"}
                    ]
                    current_step = sum(st.session_state['single_steps'].values())
                    user_feedback.show_workflow_guide(steps, current_step)
            
                elif st.session_state['workflow_type'] == 'multiple':
                    steps = [
                        {"title": "Upload Files", "description": "Select multiple files to merge"},
                        {"title": "Merge Data", "description": "Combine files with intelligent mapping"},
                        {"title": "Transform Data", "description": "Clean and standardize merged data"},
                        {"title": "Validate & Export", "description": "Verify quality and download results"}
                    ]
                    current_step = sum(st.session_state['multiple_steps'].values())
                    user_feedback.show_workflow_guide(steps, current_step)
                
                else:  # AMR analytics
                    steps = [
                        {"title": "Upload AMR Data", "description": "Upload antimicrobial susceptibility data"},
                        {"title": "Run Analysis", "description": "Generate resistance analysis and visualizations"}
                    ]
                    current_step = sum(st.session_state['amr_steps'].values())
                    user_feedback.show_workflow_guide(steps, current_step)
            
            st.markdown("---")
            st.caption("Version 2.0.0 | © 2025 The Aurum Institute")
            st.caption("[Need help?](mailto:support@auruminstitute.org)")
            
            # Performance and cache controls
            with st.expander("🔧 Advanced", expanded=False):
                if st.button("🗑️ Clear Cache", use_container_width=True):
                    clear_all_caches()
                    user_feedback.show_success("Cache cleared successfully!")
                    st.rerun()
                
                if st.button("📊 Performance Stats", use_container_width=True):
                    st.session_state.show_performance_stats = True
                    st.rerun()
        
        # Show performance stats if requested
        if st.session_state.get('show_performance_stats', False):
            from utils.performance_monitor import performance_monitor
            performance_monitor.show_performance_summary()
            
            if st.button("Close Performance Stats"):
                st.session_state.show_performance_stats = False
                st.rerun()
            return
        
        # Main content
        st.markdown('<h1 class="main-header">GLASS Data Standardizer</h1>', unsafe_allow_html=True)
        
        # Workflow Selection
        if not st.session_state['workflow_selected']:
            st.markdown('<h2 class="step-header">Choose Your Workflow</h2>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
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
            
            with col3:
                if st.button("🧬 AMR Analytics", use_container_width=True):
                    st.session_state['workflow_type'] = 'amr'
                    st.session_state['workflow_selected'] = True
                    st.rerun()
            
            st.markdown("---")
            
            # Show tips and help
            tips = [
                "Use 'Single File' for individual data files that need standardization",
                "Use 'Multiple Files' to combine and merge several files together",
                "Use 'AMR Analytics' for antimicrobial resistance analysis with CLSI compliance",
                "All workflows support CSV and Excel file formats",
                "Check the settings panel for customization options"
            ]
            user_feedback.show_tips(tips, "💡 Getting Started Tips")
            
            st.info("ℹ️ Choose your workflow: 'Standardize Single File' for one file, 'Merge Multiple Files' for combining files, or 'AMR Analytics' for antimicrobial resistance analysis.")
            return
        
        # Show progress based on selected workflow
        show_progress()
        
        # Single File Workflow
        if st.session_state['workflow_type'] == 'single':
            # Upload
            if not st.session_state['single_steps']['upload']:
                st.markdown('<h2 class="step-header">Step 1: Upload Your Data</h2>', unsafe_allow_html=True)
                
                # Show file size limit
                max_size_mb = app_settings.get_file_size_limit() / (1024 * 1024)
                st.info(f"📁 Maximum file size: {max_size_mb:.0f} MB")
                
                uploaded_df = file_handler.upload_file()
                
                if uploaded_df is not None:
                    try:
                        # Show success message
                        user_feedback.show_success(f"Successfully uploaded {len(uploaded_df)} rows with {len(uploaded_df.columns)} columns")
                        
                        # Optimize DataFrame if enabled
                        if app_settings.should_optimize_dataframes():
                            from utils.performance_monitor import performance_monitor
                            uploaded_df = performance_monitor.optimize_dataframe(uploaded_df)
                        
                        st.session_state['data'] = uploaded_df
                        st.session_state['single_steps']['upload'] = True
                        log_streamlit_action("file_upload", f"Single file workflow - {len(uploaded_df)} rows, {len(uploaded_df.columns)} columns")
                        
                        # Show data summary
                        user_feedback.show_data_summary(uploaded_df, "Uploaded Data Summary")
                        
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
                            
                    except Exception as e:
                        st.error(f"❌ Error processing uploaded data: {str(e)}")
                        st.error("Please try uploading a different file or contact support if the issue persists.")
                        if logger:
                            logger.error(f"Error processing uploaded data: {str(e)}", exc_info=True)
        
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
                try:
                    mappings, should_apply = column_mapper.show_mapping_interface(st.session_state['data'])
                    if should_apply and mappings:
                        st.session_state['data'] = column_mapper.apply_mappings(st.session_state['data'], mappings)
                        st.session_state['mapped_columns'] = mappings
                        st.session_state['single_steps']['mapping'] = True
                except Exception as e:
                    st.error(f"❌ Error during column mapping: {str(e)}")
                    st.error("Please try again or skip mapping if not needed.")
                    if logger:
                        logger.error(f"Error during column mapping: {str(e)}", exc_info=True)
            else:
                st.session_state['single_steps']['mapping'] = True
        
        # Transform (Single File)
        if st.session_state['single_steps']['mapping'] and not st.session_state['single_steps']['transform']:
            st.markdown('<h2 class="step-header">Step 3: Transform Data</h2>', unsafe_allow_html=True)
            try:
                transformed_df = transformer.show_transformation_interface(
                    st.session_state['data']
                )
                
                if transformed_df is not None:
                    st.session_state['data'] = transformed_df
                    st.session_state['single_steps']['transform'] = True
            except Exception as e:
                st.error(f"❌ Error during data transformation: {str(e)}")
                st.error("Please try again or contact support if the issue persists.")
                if logger:
                    logger.error(f"Error during data transformation: {str(e)}", exc_info=True)
        
        # Validation and Export (Single File)
        if st.session_state['single_steps']['transform']:
            st.markdown('<h2 class="step-header">Final Step: Validate and Export</h2>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Run Validation", use_container_width=True):
                    try:
                        validation_results = validator.validate_data(
                            st.session_state['data']
                        )
                        st.session_state['validation_results'] = validation_results
                        st.session_state['single_steps']['validate'] = True
                        
                        with st.expander("Validation Results", expanded=True):
                            validator.show_validation_results(validation_results)
                    except Exception as e:
                        st.error(f"❌ Error during validation: {str(e)}")
                        st.error("Please try again or contact support if the issue persists.")
                        if logger:
                            logger.error(f"Error during validation: {str(e)}", exc_info=True)
            
            with col2:
                if st.button("Export Data", use_container_width=True, type="primary"):
                    try:
                        excel_exporter.show_export_interface(
                            st.session_state['data'],
                            st.session_state.get('validation_results')
                        )
                    except Exception as e:
                        st.error(f"❌ Error during export: {str(e)}")
                        st.error("Please try again or contact support if the issue persists.")
                        if logger:
                            logger.error(f"Error during export: {str(e)}", exc_info=True)
    
        # Multiple Files Workflow
        elif st.session_state['workflow_type'] == 'multiple':
            # Upload and Merge
            if not st.session_state['multiple_steps']['upload']:
                st.markdown('<h2 class="step-header">Step 1: Upload and Merge Files</h2>', unsafe_allow_html=True)
                try:
                    merged_df = file_merger.show_merger_interface()
                    
                    if merged_df is not None:
                        st.session_state['data'] = merged_df
                        st.session_state['multiple_steps']['upload'] = True
                        st.session_state['multiple_steps']['merge'] = True
                except Exception as e:
                    st.error(f"❌ Error during file merging: {str(e)}")
                    st.error("Please try again or contact support if the issue persists.")
                    if logger:
                        logger.error(f"Error during file merging: {str(e)}", exc_info=True)
            
            # Transform (Multiple Files)
            if st.session_state['multiple_steps']['merge'] and not st.session_state['multiple_steps']['transform']:
                st.markdown('<h2 class="step-header">Step 2: Transform Data</h2>', unsafe_allow_html=True)
                try:
                    transformed_df = transformer.show_transformation_interface(
                        st.session_state['data']
                    )
                    
                    if transformed_df is not None:
                        st.session_state['data'] = transformed_df
                        st.session_state['multiple_steps']['transform'] = True
                except Exception as e:
                    st.error(f"❌ Error during data transformation: {str(e)}")
                    st.error("Please try again or contact support if the issue persists.")
                    if logger:
                        logger.error(f"Error during data transformation: {str(e)}", exc_info=True)
            
            # Validation and Export (Multiple Files)
            if st.session_state['multiple_steps']['transform']:
                st.markdown('<h2 class="step-header">Final Step: Validate and Export</h2>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Run Validation", use_container_width=True):
                        try:
                            validation_results = validator.validate_data(
                                st.session_state['data']
                            )
                            st.session_state['validation_results'] = validation_results
                            st.session_state['multiple_steps']['validate'] = True
                            
                            with st.expander("Validation Results", expanded=True):
                                validator.show_validation_results(validation_results)
                        except Exception as e:
                            st.error(f"❌ Error during validation: {str(e)}")
                            st.error("Please try again or contact support if the issue persists.")
                            if logger:
                                logger.error(f"Error during validation: {str(e)}", exc_info=True)
                
                with col2:
                    if st.button("Export Data", use_container_width=True, type="primary"):
                        try:
                            excel_exporter.show_export_interface(
                                st.session_state['data'],
                                st.session_state.get('validation_results')
                            )
                        except Exception as e:
                            st.error(f"❌ Error during export: {str(e)}")
                            st.error("Please try again or contact support if the issue persists.")
                            if logger:
                                logger.error(f"Error during export: {str(e)}", exc_info=True)
    
        # AMR Analytics Workflow
        elif st.session_state['workflow_type'] == 'amr':
            try:
                # Choose between standard and enhanced AMR interface
                if st.sidebar.checkbox("🔬 Enhanced Scientific Analysis", value=True, 
                                      help="Enable advanced statistical analysis with confidence intervals"):
                    enhanced_amr_interface = EnhancedAMRInterface()
                    enhanced_amr_interface.render_enhanced_amr_analysis_page()
                else:
                    amr_interface = AMRInterface()
                    amr_interface.render_amr_analysis_page()
            except Exception as e:
                st.error(f"❌ Error in AMR Analytics: {str(e)}")
                st.error("Please try again or contact support if the issue persists.")
                if logger:
                    logger.error(f"Error in AMR Analytics: {str(e)}", exc_info=True)
        
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
                for key in st.session_state['amr_steps']:
                    st.session_state['amr_steps'][key] = False
                    
                st.rerun()
    
    except Exception as e:
        st.error(f"❌ Application error: {str(e)}")
        st.error("Please refresh the page and try again. If the problem persists, contact support.")
        if logger:
            logger.error(f"Application error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
