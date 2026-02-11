"""
AMR Data Harmonizer v2.0.0
Main application module for data standardization and AMR analysis.

This module provides a comprehensive web interface for:
- Single file data standardization
- Multiple file merging and processing
- Antimicrobial resistance (AMR) analysis
- Data validation and quality assessment
- Export functionality

Author: AMR Data Harmonizer Team
Version: 2.0.0
"""

import streamlit as st
import pandas as pd

# Import utilities with error handling
# Store imported classes in a dict for verification
_imported_classes = {}

try:
    from utils.file_handler import FileHandler
    _imported_classes['FileHandler'] = FileHandler
    from utils.schema_analyzer import SchemaAnalyzer
    _imported_classes['SchemaAnalyzer'] = SchemaAnalyzer
    from utils.column_mapper import ColumnMapper
    _imported_classes['ColumnMapper'] = ColumnMapper
    from utils.transformer import DataTransformer
    _imported_classes['DataTransformer'] = DataTransformer
    from utils.validator import DataValidator
    _imported_classes['DataValidator'] = DataValidator
    from utils.excel_exporter import ExcelExporter
    _imported_classes['ExcelExporter'] = ExcelExporter
    from utils.file_merger import FileMerger
    _imported_classes['FileMerger'] = FileMerger
    from utils.data_quality import DataQualityAssessor
    _imported_classes['DataQualityAssessor'] = DataQualityAssessor
    from utils.data_profiler import DataProfiler
    _imported_classes['DataProfiler'] = DataProfiler
    from utils.amr_interface import AMRInterface
    _imported_classes['AMRInterface'] = AMRInterface
    from utils.enhanced_amr_interface import EnhancedAMRInterface
    _imported_classes['EnhancedAMRInterface'] = EnhancedAMRInterface
    from utils.logger import log_streamlit_action
    from utils.app_config import app_config
    from utils.user_feedback import user_feedback
    from utils.app_settings import app_settings
    from utils.cache_manager import clear_all_caches
    from utils.production_logger import initialize_production_logger, get_production_logger
    from config.production import production_config
    from utils.ui_validator import ui_validator
    _imported_classes['ui_validator'] = ui_validator
except ImportError as e:
    st.error(f"❌ Failed to import required modules: {str(e)}")
    st.error("Please ensure all dependencies are installed: pip install -r requirements.txt")
    import traceback
    with st.expander("🔍 Detailed Error Information"):
        st.code(traceback.format_exc())
    st.stop()
except Exception as e:
    st.error(f"❌ Unexpected error during imports: {str(e)}")
    import traceback
    with st.expander("🔍 Detailed Error Information"):
        st.code(traceback.format_exc())
    st.stop()

# Helper function to safely use ui_validator
def safe_ui_validator_call(method_name, *args, **kwargs):
    """Safely call ui_validator methods with fallback"""
    try:
        if 'ui_validator' in _imported_classes:
            validator = _imported_classes['ui_validator']
            method = getattr(validator, method_name, None)
            if method:
                return method(*args, **kwargs)
    except Exception:
        pass  # Silently fail, use fallback
    return None

# Configure Streamlit page
st.set_page_config(
    page_title="AMR Data Harmonizer",
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

# Enhanced custom styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .step-header {
        font-size: 1.8rem;
        font-weight: 600;
        margin: 1.5rem 0;
        color: #212529;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #007bff;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #cce5ff;
        border: 1px solid #b8daff;
        color: #004085;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button {
        border-radius: 8px;
        transition: all 0.3s ease;
        font-weight: 600;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .workflow-container {
        padding: 2rem 0;
    }
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def show_progress():
    """Display enhanced progress indicator with step visualization."""
    if not st.session_state['workflow_selected']:
        return
    
    from utils.ui_components import ui_components
    
    if st.session_state['workflow_type'] == 'single':
        steps = st.session_state['single_steps']
        progress = sum(steps.values()) / len(steps)
        
        step_list = [
            {"title": "Upload", "icon": "📤"},
            {"title": "Map", "icon": "🔗"},
            {"title": "Transform", "icon": "🔧"},
            {"title": "Validate", "icon": "✔️"}
        ]
        
        completed = []
        current = 0
        if steps['upload']:
            completed.append(0)
            current = 1
        if steps['mapping']:
            completed.append(1)
            current = 2
        if steps['transform']:
            completed.append(2)
            current = 3
        if steps['validate']:
            completed.append(3)
            current = 4
        
        ui_components.step_indicator(step_list, current, completed)
        st.progress(progress)
    
    elif st.session_state['workflow_type'] == 'multiple':
        steps = st.session_state['multiple_steps']
        progress = sum(steps.values()) / len(steps)
        
        step_list = [
            {"title": "Upload", "icon": "📤"},
            {"title": "Merge", "icon": "🔄"},
            {"title": "Transform", "icon": "🔧"},
            {"title": "Validate", "icon": "✔️"}
        ]
        
        completed = []
        current = 0
        if steps['upload']:
            completed.append(0)
            current = 1
        if steps['merge']:
            completed.append(1)
            current = 2
        if steps['transform']:
            completed.append(2)
            current = 3
        if steps['validate']:
            completed.append(3)
            current = 4
        
        ui_components.step_indicator(step_list, current, completed)
        st.progress(progress)
    
    elif st.session_state['workflow_type'] == 'glass':
        # GLASS wizard has its own step indicator, don't show progress here
        pass
    elif st.session_state['workflow_type'] == 'whonet':
        # WHONET wizard has its own step indicator, don't show progress here
        pass
    
    else:  # AMR analytics workflow
        steps = st.session_state['amr_steps']
        progress = sum(steps.values()) / len(steps)
        
        step_list = [
            {"title": "Upload Data", "icon": "📤"},
            {"title": "AMR Analysis", "icon": "🧬"}
        ]
        
        completed = []
        current = 0
        if steps['upload']:
            completed.append(0)
            current = 1
        if steps['analyze']:
            completed.append(1)
            current = 2
        
        ui_components.step_indicator(step_list, current, completed)
        st.progress(progress)

def _show_introduction():
    """
    Display introduction section explaining what the app is and the problems it solves.
    """
    st.markdown("---")
    
    # Hero Section
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 10px; margin-bottom: 2rem; color: white;'>
        <h2 style='color: white; margin-bottom: 1rem;'>🏥 Welcome to AMR Data Harmonizer</h2>
        <p style='font-size: 1.1rem; line-height: 1.6; color: white;'>
            A comprehensive platform designed to address critical data cleaning challenges in 
            <strong>Antimicrobial Resistance (AMR) surveillance</strong> across African laboratories.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Problem Statement
    st.markdown("### 🔍 The Challenge")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### Common Data Quality Issues in African AMR Surveillance:
        
        - **📊 Inconsistent Data Collection**
          - Varied formats and structures across laboratories
          - Different naming conventions for organisms and antimicrobials
          - Inconsistent date formats and data entry practices
        
        - **🔬 Limited Laboratory Capacity**
          - Manual data entry leading to errors
          - Lack of standardized reporting formats
          - Limited quality assurance processes
        
        - **📁 Fragmented Data Management**
          - Data stored in multiple systems and formats
          - Difficulty in merging data from different sources
          - Lack of data harmonization
        """)
    
    with col2:
        st.markdown("""
        #### Impact on Global Surveillance:
        
        - **🚫 Submission Barriers**
          - Data doesn't meet GLASS (Global Antimicrobial Resistance and Use Surveillance System) requirements
          - Incompatible with WHONET format
          - Missing required fields and validation failures
        
        - **📉 Reduced Data Quality**
          - Incomplete datasets
          - Inconsistent organism names and antimicrobial results
          - Missing critical metadata
        
        - **⏱️ Time-Consuming Manual Work**
          - Hours spent on data cleaning and standardization
          - High risk of human error
          - Delayed submission to global surveillance systems
        """)
    
    st.markdown("---")
    
    # Solution Section
    st.markdown("### ✨ How AMR Data Harmonizer Solves These Problems")
    
    solution_cols = st.columns(3)
    
    with solution_cols[0]:
        st.markdown("""
        #### 🧹 **Intelligent Data Cleaning**
        
        - **Automatic Detection**: Identifies AMR-specific columns (organisms, antimicrobials, specimens)
        - **Flexible Cleaning**: Handles various data formats and edge cases
        - **Standardization**: Normalizes organism names, antimicrobial results, and specimen types
        - **Edge Case Handling**: Manages encoding issues, delimiters, merged cells, and more
        """)
    
    with solution_cols[1]:
        st.markdown("""
        #### 🔗 **Smart Data Integration**
        
        - **Multi-File Merging**: Intelligently combines data from multiple sources
        - **Column Mapping**: Automatic matching with fuzzy logic
        - **Data Harmonization**: Resolves inconsistencies across datasets
        - **Quality Validation**: Ensures merged data meets standards
        """)
    
    with solution_cols[2]:
        st.markdown("""
        #### 📤 **Global Submission Ready**
        
        - **GLASS Preparation**: Wizard-guided preparation for GLASS submission
        - **WHONET Compatibility**: Standardizes data for WHONET import
        - **Quality Assessment**: Comprehensive data quality scoring
        - **Export Options**: Multiple formats (CSV, Excel, JSON, XML)
        """)
    
    st.markdown("---")
    
    # Key Features
    st.markdown("### 🎯 Key Features")
    
    feature_cols = st.columns(2)
    
    with feature_cols[0]:
        st.markdown("""
        - ✅ **Flexible AMR Data Cleaning**
          - Automatic organism name standardization
          - Antimicrobial result normalization (S/R/I/ND/NM)
          - Specimen type standardization
          - Date format handling
          - Age extraction from text
        
        - ✅ **Robust File Processing**
          - Multiple encoding support (UTF-8, Latin-1, CP1252, etc.)
          - Automatic delimiter detection
          - Handles empty files, multiple sheets, merged cells
          - Footer/summary row removal
        """)
    
    with feature_cols[1]:
        st.markdown("""
        - ✅ **Advanced Analytics**
          - AMR resistance analysis with statistical validation
          - Antibiogram generation
          - Data quality assessment
          - Professional visualizations
        
        - ✅ **Production Ready**
          - Comprehensive error handling
          - Health monitoring
          - Security validation
          - Performance optimization
        """)
    
    st.markdown("---")
    
    # Use Cases
    st.markdown("### 💼 Who Can Benefit?")
    
    use_case_cols = st.columns(3)
    
    with use_case_cols[0]:
        st.markdown("""
        **🏥 Laboratory Staff**
        - Clean and standardize daily lab data
        - Prepare data for submission
        - Generate quality reports
        """)
    
    with use_case_cols[1]:
        st.markdown("""
        **📊 Data Managers**
        - Merge data from multiple sources
        - Harmonize inconsistent datasets
        - Ensure data quality standards
        """)
    
    with use_case_cols[2]:
        st.markdown("""
        **🔬 Researchers**
        - Prepare data for analysis
        - Generate AMR analytics
        - Export publication-ready reports
        """)
    
    st.markdown("---")
    
    # Call to Action
    st.markdown("""
    <div style='background-color: #000000; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #667eea;'>
        <h3 style='margin-top: 0;'>🚀 Ready to Get Started?</h3>
        <p style='margin-bottom: 0.5rem;'>
            Choose a workflow below to begin processing your AMR surveillance data. 
            The tool will guide you through each step with clear instructions.
        </p>
        <p style='margin-bottom: 0; font-size: 0.9rem; color: #666;'>
            <strong>💡 Tip:</strong> Start with "Merge Multiple Files" if you have data from multiple sources, 
            or "Standardize Single File" for individual file processing.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

def main():
    """
    Main application function that orchestrates the AMR Data Harmonizer workflow.
    
    This function provides a comprehensive data standardization platform with:
    - Single file processing workflow
    - Multiple file merging capabilities
    - Advanced AMR analytics with statistical validation
    - Real-time data validation and quality assessment
    - Professional export functionality
    - Production-ready error handling and monitoring
    
    The application supports three main workflows:
    1. Single File: Upload → Map → Transform → Validate → Export
    2. Multiple Files: Upload → Merge → Transform → Validate → Export
    3. AMR Analytics: Upload → Analyze → Generate Reports → Export
    
    Features:
    - Intelligent column mapping with fuzzy matching
    - Data type detection and conversion
    - Statistical analysis with confidence intervals
    - Production error handling and recovery
    - Health monitoring and metrics
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
            if logger:
                logger.log_application_start(production_config.version, production_config.environment)
        except Exception as e:
            st.warning(f"⚠️ Production logging not available: {str(e)}")
            logger = None
        
        # Initialize components with error handling
        # Verify imports are available
        if 'FileHandler' not in _imported_classes:
            st.error("❌ FileHandler was not imported successfully. Please check the error messages above.")
            return
        
        try:
            # Initialize components one by one for better error reporting
            # Use the verified imported class
            FileHandlerClass = _imported_classes['FileHandler']
            file_handler = FileHandlerClass()
            
            try:
                schema_analyzer = SchemaAnalyzer()
            except Exception as e:
                st.error(f"❌ Failed to initialize SchemaAnalyzer: {str(e)}")
                raise
            
            try:
                column_mapper = ColumnMapper()
            except Exception as e:
                st.error(f"❌ Failed to initialize ColumnMapper: {str(e)}")
                raise
            
            try:
                transformer = DataTransformer()
            except Exception as e:
                st.error(f"❌ Failed to initialize DataTransformer: {str(e)}")
                raise
            
            try:
                validator = DataValidator()
            except Exception as e:
                st.error(f"❌ Failed to initialize DataValidator: {str(e)}")
                raise
            
            try:
                if 'ExcelExporter' not in _imported_classes:
                    st.error("❌ ExcelExporter was not imported successfully.")
                    raise ImportError("ExcelExporter not available")
                ExcelExporterClass = _imported_classes['ExcelExporter']
                excel_exporter = ExcelExporterClass()
            except Exception as e:
                st.error(f"❌ Failed to initialize ExcelExporter: {str(e)}")
                raise
            
            try:
                file_merger = FileMerger()
            except Exception as e:
                st.error(f"❌ Failed to initialize FileMerger: {str(e)}")
                raise
            
            try:
                quality_assessor = DataQualityAssessor()
            except Exception as e:
                st.error(f"❌ Failed to initialize DataQualityAssessor: {str(e)}")
                raise
            
            try:
                data_profiler = DataProfiler()
            except Exception as e:
                st.error(f"❌ Failed to initialize DataProfiler: {str(e)}")
                raise
                
        except Exception as e:
            import traceback
            st.error(f"❌ Failed to initialize application components: {str(e)}")
            st.error("Please check your installation and try again.")
            with st.expander("🔍 Detailed Error Information"):
                st.code(traceback.format_exc())
            return
        
        # Sidebar with logo and essential info
        with st.sidebar:
            # Try to load logo, use fallback if not found (for cloud deployment)
            logo_paths = [
                "Png/Veraya (2).png",
                "Png/Veraya (1).png",
                "Png/Veraya (3).png"
            ]
            logo_loaded = False
            for logo_path in logo_paths:
                try:
                    import os
                    if os.path.exists(logo_path):
                        st.image(logo_path, width=200)
                        logo_loaded = True
                        break
                except:
                    continue
            
            if not logo_loaded:
                # Fallback: Use emoji or text logo
                st.markdown("## 🏥 GLASS Data Standardizer")
            else:
                st.markdown("## GLASS Data Standardizer")
            
            # Add accessibility improvements (if available)
            try:
                if 'ui_validator' in _imported_classes:
                    _imported_classes['ui_validator'].show_accessible_labels()
            except (NameError, AttributeError, Exception):
                pass  # Non-critical, continue without it
            
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
                    user_feedback.show_workflow_guide(steps, current_step, background_color="#000000")
            
            st.markdown("---")
            st.caption("Version 2.0.0 | © 2025 Veraya Health Technologies")
            st.caption("[Need help?](mailto:mikekay262@gmail.com)")
            
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
        st.markdown('<h1 class="main-header">AMR Data Harmonizer</h1>', unsafe_allow_html=True)
        
        # Introduction Section
        if not st.session_state.get('workflow_selected', False):
            _show_introduction()
        
        # Enhanced Workflow Selection
        if not st.session_state['workflow_selected']:
            from utils.ui_components import ui_components
            
            st.markdown('<h2 class="step-header">Choose Your Workflow</h2>', unsafe_allow_html=True)
            st.markdown("Select the workflow that best fits your data processing needs:")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if ui_components.workflow_card(
                    title="Standardize Single File",
                    description="Process and standardize individual data files with mapping, transformation, and validation.",
                    icon="📄",
                    features=[
                        "Column mapping & renaming",
                        "Data transformation",
                        "Quality validation",
                        "Multi-format export"
                    ],
                    button_label="Start Single File Workflow",
                    button_key="workflow_single",
                    recommended=False
                ):
                    st.session_state['workflow_type'] = 'single'
                    st.session_state['workflow_selected'] = True
                    st.rerun()
            
            with col2:
                if ui_components.workflow_card(
                    title="Merge Multiple Files",
                    description="Intelligently combine multiple files with automatic column mapping and data harmonization.",
                    icon="📚",
                    features=[
                        "Smart column matching",
                        "Automatic data merging",
                        "Duplicate detection",
                        "Unified export"
                    ],
                    button_label="Start Merge Workflow",
                    button_key="workflow_multiple",
                    recommended=True
                ):
                    st.session_state['workflow_type'] = 'multiple'
                    st.session_state['workflow_selected'] = True
                    st.rerun()
            
            with col3:
                if ui_components.workflow_card(
                    title="AMR Analytics",
                    description="Advanced antimicrobial resistance analysis with CLSI compliance and statistical validation.",
                    icon="🧬",
                    features=[
                        "CLSI-compliant analysis",
                        "Resistance rate calculations",
                        "Professional visualizations",
                        "Statistical reports"
                    ],
                    button_label="Start AMR Analysis",
                    button_key="workflow_amr",
                    recommended=False
                ):
                    st.session_state['workflow_type'] = 'amr'
                    st.session_state['workflow_selected'] = True
                    st.rerun()
            
            # Add GLASS and WHONET Preparation Wizards as prominent options
            st.markdown("---")
            st.markdown("### 🎯 **Data Preparation Wizards**")
            st.markdown("""
            **Perfect for non-technical users!** Step-by-step guided processes to prepare your AMR data.
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                if ui_components.workflow_card(
                    title="GLASS Preparation Wizard",
                    description="Step-by-step guided process to clean, standardize, and prepare your AMR data for GLASS submission. No programming required!",
                    icon="🧬",
                    features=[
                        "Automatic data cleaning",
                        "GLASS format standardization",
                        "Step-by-step guidance",
                        "Built-in validation",
                        "Ready for submission"
                    ],
                    button_label="Start GLASS Wizard",
                    button_key="workflow_glass",
                    recommended=True
                ):
                    st.session_state['workflow_type'] = 'glass'
                    st.session_state['workflow_selected'] = True
                    st.rerun()
            
            with col2:
                if ui_components.workflow_card(
                    title="WHONET Preparation Wizard",
                    description="Step-by-step guided process to clean, standardize, and prepare your AMR data for WHONET import. No programming required!",
                    icon="🔬",
                    features=[
                        "Automatic data cleaning",
                        "WHONET format standardization",
                        "Comprehensive quality reports",
                        "Built-in validation",
                        "Ready for WHONET import"
                    ],
                    button_label="Start WHONET Wizard",
                    button_key="workflow_whonet",
                    recommended=True
                ):
                    st.session_state['workflow_type'] = 'whonet'
                    st.session_state['workflow_selected'] = True
                    st.rerun()
            
            st.info("""
            **Why use the wizards?**
            - ✅ No technical knowledge needed
            - ✅ Automatic fixes for common issues
            - ✅ Validates against format requirements
            - ✅ Guided step-by-step process
            - ✅ Comprehensive data quality reports
            """)
            
            # Add quick start guide
            with st.expander("🚀 Quick Start Guide", expanded=False):
                st.markdown("""
                **First time using this tool?**
                
                1. **Choose your workflow** based on what you need:
                   - **Wizards** (recommended for beginners): Step-by-step guidance
                   - **Single File**: Process one file at a time
                   - **Multiple Files**: Merge and combine files
                   - **AMR Analytics**: Analyze resistance patterns
                
                2. **Upload your data** - CSV or Excel files work best
                
                3. **Follow the steps** - The tool will guide you through each step
                
                4. **Review quality reports** - Check data quality before exporting
                
                5. **Export your data** - Download cleaned, standardized data
                
                **Need help?** Click the help icons (❓) throughout the interface for guidance.
                """)
            
            st.markdown("---")
            
            # Enhanced tips section
            with st.expander("💡 Getting Started Tips", expanded=False):
                tips = [
                    "**Single File Workflow**: Best for processing individual files that need standardization and cleaning",
                    "**Multiple Files Workflow**: Ideal for combining data from different sources with varying formats",
                    "**AMR Analytics**: Specialized workflow for antimicrobial resistance data analysis and reporting",
                    "All workflows support CSV and Excel (.xlsx, .xls) file formats",
                    "Check the settings panel (sidebar) for customization options and file size limits",
                    "Use the 'Start New Process' button to switch between workflows anytime"
                ]
                for tip in tips:
                    st.markdown(f"- {tip}")
            
            ui_components.info_banner(
                "💡 **Tip**: Start with the 'Merge Multiple Files' workflow if you're unsure - it's the most versatile option!",
                type="info"
            )
            return
        
        # Show progress based on selected workflow
        show_progress()
        
        # Single File Workflow
        if st.session_state['workflow_type'] == 'single':
            # Upload
            if not st.session_state['single_steps']['upload']:
                from utils.ui_components import ui_components
                ui_components.section_header(
                    "Step 1: Upload Your Data",
                    icon="📤",
                    description="Select and upload your data file for processing"
                )
                
                # Show file size limit with better styling
                max_size_mb = app_settings.get_file_size_limit() / (1024 * 1024)
                ui_components.info_banner(
                    f"Maximum file size: **{max_size_mb:.0f} MB** | Supported formats: CSV, Excel (.xlsx, .xls)",
                    type="info",
                    icon="📁"
                )
                
                # Enhanced file upload with validation
                safe_ui_validator_call('show_workflow_guidance', 'single')
                
                uploaded_file = st.file_uploader(
                    "Upload your data file",
                    type=['csv', 'xlsx', 'xls'],
                    help="Supported formats: CSV, Excel (.xlsx, .xls). Maximum file size: 100 MB"
                )
                
                if uploaded_file is not None:
                    # Validate file before processing (with fallback)
                    validation_result = {'valid': True, 'errors': [], 'warnings': []}
                    try:
                        if 'ui_validator' in _imported_classes:
                            validation_result = _imported_classes['ui_validator'].validate_file_upload(uploaded_file)
                    except Exception:
                        pass
                    
                    if validation_result.get('errors'):
                        for error in validation_result['errors']:
                            st.error(f"❌ {error}")
                        uploaded_df = None
                    else:
                        # Show warnings if any
                        if validation_result.get('warnings'):
                            for warning in validation_result['warnings']:
                                st.warning(f"⚠️ {warning}")
                        
                        # Process file using FileHandler (production-ready with edge case handling)
                        with st.spinner("Loading and processing file..."):
                            try:
                                # Use FileHandler for robust file processing
                                file_handler = _imported_classes['FileHandler']()
                                uploaded_file.seek(0)  # Reset file pointer
                                uploaded_df = file_handler._process_uploaded_file(uploaded_file)
                            except Exception as e:
                                st.error(f"❌ Failed to process uploaded file: {str(e)}")
                                safe_ui_validator_call('show_operation_feedback',
                                                      "File Upload", "error", 
                                                      "Failed to process uploaded file.",
                                                      details=str(e))
                                uploaded_df = None
                else:
                    uploaded_df = None
                
                if uploaded_df is not None:
                    try:
                        # Validate dataframe (with fallback)
                        df_validation = {'valid': True, 'errors': [], 'warnings': [], 'suggestions': []}
                        try:
                            if 'ui_validator' in _imported_classes:
                                df_validation = _imported_classes['ui_validator'].validate_dataframe_for_processing(uploaded_df)
                        except Exception:
                            pass
                        
                        if not df_validation.get('valid', True):
                            for error in df_validation.get('errors', []):
                                st.error(f"❌ {error}")
                            uploaded_df = None
                        else:
                            # Show warnings and suggestions
                            if df_validation.get('warnings'):
                                for warning in df_validation['warnings']:
                                    st.warning(f"⚠️ {warning}")
                            
                            if df_validation['suggestions']:
                                for suggestion in df_validation['suggestions']:
                                    st.info(f"💡 {suggestion}")
                            
                            # Show success message
                            if uploaded_df is not None:
                                user_feedback.show_success(f"Successfully uploaded {len(uploaded_df)} rows with {len(uploaded_df.columns)} columns")
                            
                            # Optimize DataFrame if enabled
                            if uploaded_df is not None and app_settings.should_optimize_dataframes():
                                from utils.performance_monitor import performance_monitor
                                uploaded_df = performance_monitor.optimize_dataframe(uploaded_df)
                            
                            if uploaded_df is not None:
                                st.session_state['data'] = uploaded_df
                                st.session_state['single_steps']['upload'] = True
                                log_streamlit_action("file_upload", f"Single file workflow - {len(uploaded_df)} rows, {len(uploaded_df.columns)} columns")
                        
                            # Show data summary
                            if uploaded_df is not None:
                                user_feedback.show_data_summary(uploaded_df, "Uploaded Data Summary")
                                
                                # Enhanced data preview with guidance
                                preview_result = safe_ui_validator_call('show_data_preview_with_guidance', uploaded_df, "Data Preview")
                                if preview_result is None:
                                    # Fallback: simple preview
                                    st.write("### Data Preview")
                                    st.dataframe(uploaded_df.head(10), use_container_width=True)
                                
                                with st.expander("📋 Column Information", expanded=False):
                                    schema_info = schema_analyzer.analyze_schema(uploaded_df)
                                    st.json(schema_info)
                                    
                                    safe_ui_validator_call('show_contextual_help',
                                        "Understanding Column Information",
                                        """
                                        **Column Information shows:**
                                        - Data types (text, numbers, dates)
                                        - Number of non-empty values
                                        - Sample values
                                        
                                        **What to check:**
                                        - Ensure data types are correct
                                        - Verify column names match your expectations
                                        - Check for columns with many missing values
                                        """
                                    )
                                
                                # Add data quality assessment
                                with st.expander("📊 Data Quality Assessment", expanded=False):
                                    quality_results = quality_assessor.assess_data_quality(uploaded_df)
                                    quality_assessor.show_quality_report(quality_results)
                                
                                # Add AMR-specific quality assessment if AMR data detected
                                from utils.amr_data_quality import AMRDataQuality
                                amr_quality = AMRDataQuality()
                                
                                # Detect if this is AMR data
                                is_amr_data = any(col.lower() in ['organism', 'specimen', 'antimicrobial', 'sir', '_nd', '_nm'] 
                                                for col in uploaded_df.columns)
                        
                                if is_amr_data:
                                    with st.expander("🧬 AMR Data Quality Assessment (African Context)", expanded=True):
                                        amr_report = amr_quality.assess_amr_data_quality(uploaded_df, context='glass')
                                        amr_quality.display_amr_quality_report(amr_report)
                                        
                                        # Auto-fix option
                                        if amr_report.get('quality_score', 0) < 80 or not amr_report.get('glass_submission_ready', False):
                                            st.markdown("### 🔧 Auto-Fix Options")
                                            col1, col2, col3 = st.columns(3)
                                            
                                            with col1:
                                                fix_organisms = st.button("🔬 Fix Organism Names", 
                                                                          help="Standardize organism names to GLASS format")
                                            with col2:
                                                fix_dates = st.button("📅 Fix Date Formats", 
                                                                      help="Standardize date formats")
                                            with col3:
                                                fix_completeness = st.button("✅ Improve Completeness", 
                                                                             help="Apply smart imputation for missing values")
                                            
                                            if fix_organisms:
                                                uploaded_df = amr_quality._auto_fix_organisms(uploaded_df)
                                                st.session_state['data'] = uploaded_df
                                                st.success("✅ Organism names standardized!")
                                                st.rerun()
                                            
                                            if fix_dates:
                                                uploaded_df = amr_quality._auto_fix_dates(uploaded_df)
                                                st.session_state['data'] = uploaded_df
                                                st.success("✅ Date formats standardized!")
                                                st.rerun()
                                            
                                            if fix_completeness:
                                                uploaded_df = amr_quality._auto_fix_completeness(uploaded_df)
                                                st.session_state['data'] = uploaded_df
                                                st.success("✅ Data completeness improved!")
                                                st.rerun()
                                            
                                            # Comprehensive auto-fix
                                            st.markdown("---")
                                            if st.button("🚀 Apply All Auto-Fixes", type="primary", use_container_width=True):
                                                with st.spinner("Applying comprehensive auto-fixes..."):
                                                    uploaded_df = amr_quality.comprehensive_auto_fix(uploaded_df)
                                                    st.session_state['data'] = uploaded_df
                                                    st.success("✅ All auto-fixes applied! Re-assessing quality...")
                                                    st.rerun()
                                
                                # Add data profiling
                                if uploaded_df is not None:
                                    with st.expander("🔍 Data Profile", expanded=False):
                                        profile_results = data_profiler.profile_dataframe(uploaded_df)
                                        data_profiler.show_profile_report(profile_results)
                            
                    except Exception as e:
                        ui_validator.show_operation_feedback(
                            "Data Processing", "error",
                            "An error occurred while processing your data.",
                            details=f"Error: {str(e)}\n\nPlease try:\n1. Checking your file format\n2. Ensuring the file is not corrupted\n3. Contacting support if the issue persists"
                        )
                        if logger:
                            logger.log_error(e, context="Error processing uploaded data")
        
        # Optional Mapping
        if st.session_state['single_steps']['upload'] and not st.session_state['single_steps']['mapping']:
            from utils.ui_components import ui_components
            ui_components.section_header(
                "Step 2: Column Mapping (Optional)",
                icon="🔗",
                description="Map your columns to standard names for better data consistency"
            )
            
            # Show current column names with guidance
            st.write("### Current Column Names")
            cols_df = pd.DataFrame({'Column Name': st.session_state['data'].columns})
            st.dataframe(cols_df, use_container_width=True)
            
            safe_ui_validator_call('show_contextual_help',
                "Column Mapping",
                """
                **Column Mapping helps:**
                - Standardize column names across different files
                - Match your columns to expected formats (e.g., GLASS, WHONET)
                - Improve data consistency
                
                **When to use:**
                - Your column names don't match standard formats
                - You're preparing data for specific systems (GLASS, WHONET)
                - You want to rename columns for clarity
                
                **When to skip:**
                - Your column names are already standardized
                - You're just cleaning data values, not structure
                """
            )
            
            col1, col2 = st.columns([3, 1])
            with col1:
                needs_mapping = st.radio(
                    "Do you need to map these columns to standard names?",
                    ["Yes", "No, skip mapping"],
                    horizontal=True,
                    help="Select 'Yes' if you want to rename columns to match standard formats"
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
                        logger.log_error(e, context="Error during column mapping")
            else:
                st.session_state['single_steps']['mapping'] = True
        
        # Transform (Single File)
        if st.session_state['single_steps']['mapping'] and not st.session_state['single_steps']['transform']:
            from utils.ui_components import ui_components
            ui_components.section_header(
                "Step 3: Transform Data",
                icon="🔧",
                description="Clean, standardize, and transform your data values"
            )
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
                    logger.log_error(e, context="Error during data transformation")
        
        # Validation and Export (Single File)
        if st.session_state['single_steps']['transform']:
            from utils.ui_components import ui_components
            ui_components.section_header(
                "Final Step: Validate and Export",
                icon="✔️",
                description="Verify data quality and export your processed data"
            )
            
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                if ui_components.quick_action_button(
                    "Run Validation",
                    "✔️",
                    "validate_single",
                    "Validate data quality and completeness",
                    "primary"
                ):
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
                            logger.log_error(e, context="Error during validation")
            
            with col2:
                if ui_components.quick_action_button(
                    "Export Data",
                    "📥",
                    "export_single",
                    "Download processed data in your preferred format",
                    "primary"
                ):
                    try:
                        excel_exporter.show_export_interface(
                            st.session_state['data'],
                            st.session_state.get('validation_results')
                        )
                    except Exception as e:
                        st.error(f"❌ Error during export: {str(e)}")
                        st.error("Please try again or contact support if the issue persists.")
                        if logger:
                            logger.log_error(e, context="Error during export")
    
            # Multiple Files Workflow
        elif st.session_state['workflow_type'] == 'multiple':
            # Upload and Merge
            if not st.session_state['multiple_steps']['upload']:
                from utils.ui_components import ui_components
                ui_components.section_header(
                    "Step 1: Upload and Merge Files",
                    icon="📚",
                    description="Upload multiple files and merge them with intelligent column mapping"
                )
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
                        logger.log_error(e, context="Error during file merging")
            
            # Transform (Multiple Files)
            if st.session_state['multiple_steps']['merge'] and not st.session_state['multiple_steps']['transform']:
                from utils.ui_components import ui_components
                ui_components.section_header(
                    "Step 2: Transform Data",
                    icon="🔧",
                    description="Clean and standardize the merged dataset"
                )
                
                # Add AMR quality assessment for merged data
                from utils.amr_data_quality import AMRDataQuality
                amr_quality = AMRDataQuality()
                
                is_amr_data = any(col.lower() in ['organism', 'specimen', 'antimicrobial', 'sir', '_nd', '_nm'] 
                                for col in st.session_state['data'].columns)
                
                if is_amr_data:
                    with st.expander("🧬 AMR Data Quality Assessment (Merged Data)", expanded=True):
                        amr_report = amr_quality.assess_amr_data_quality(st.session_state['data'], context='glass')
                        amr_quality.display_amr_quality_report(amr_report)
                        
                        # Auto-fix option
                        if amr_report.get('quality_score', 0) < 80 or not amr_report.get('glass_submission_ready', False):
                            st.markdown("### 🔧 Auto-Fix Options")
                            if st.button("🚀 Apply All Auto-Fixes", type="primary", use_container_width=True):
                                with st.spinner("Applying comprehensive auto-fixes to merged data..."):
                                    fixed_df = amr_quality.comprehensive_auto_fix(st.session_state['data'])
                                    st.session_state['data'] = fixed_df
                                    st.success("✅ All auto-fixes applied to merged data!")
                                    st.rerun()
                
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
                        logger.log_error(e, context="Error during data transformation")
            
            # Validation and Export (Multiple Files)
            if st.session_state['multiple_steps']['transform']:
                from utils.ui_components import ui_components
                ui_components.section_header(
                    "Final Step: Validate and Export",
                    icon="✔️",
                    description="Verify merged data quality and export results"
                )
                
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    if ui_components.quick_action_button(
                        "Run Validation",
                        "✔️",
                        "validate_multiple",
                        "Validate merged data quality",
                        "primary"
                    ):
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
                                logger.log_error(e, context="Error during validation")
                
                with col2:
                    if ui_components.quick_action_button(
                        "Export Data",
                        "📥",
                        "export_multiple",
                        "Download merged data",
                        "primary"
                    ):
                        try:
                            excel_exporter.show_export_interface(
                                st.session_state['data'],
                                st.session_state.get('validation_results')
                            )
                        except Exception as e:
                            st.error(f"❌ Error during export: {str(e)}")
                            st.error("Please try again or contact support if the issue persists.")
                            if logger:
                                logger.log_error(e, context="Error during export")
    
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
                    amr_interface.render_enhanced_amr_analysis_page()
            except Exception as e:
                st.error(f"❌ Error in AMR Analytics: {str(e)}")
                st.error("Please try again or contact support if the issue persists.")
                if logger:
                    logger.log_error(e, context="Error in AMR Analytics")
        
        # GLASS Preparation Wizard Workflow
        elif st.session_state['workflow_type'] == 'glass':
            try:
                from utils.glass_wizard import GLASSWizard
                from utils.file_handler import FileHandler
                
                glass_wizard = GLASSWizard()
                file_handler = FileHandler()
                
                # Check if data is already uploaded
                if 'wizard_df' not in st.session_state or st.session_state.get('wizard_df') is None:
                    from utils.ui_components import ui_components
                    ui_components.section_header(
                        "GLASS Data Preparation Wizard",
                        icon="🧬",
                        description="Upload your AMR data file to begin the guided preparation process"
                    )
                    
                    ui_components.info_banner(
                        "📋 **What you need:** A CSV or Excel file with your AMR data (organism names, antimicrobial results, patient information, etc.)",
                        type="info"
                    )
                    
                    uploaded_df = file_handler.upload_file()
                    
                    if uploaded_df is not None:
                        st.session_state['wizard_df'] = uploaded_df
                        st.session_state['wizard_started'] = True
                        st.rerun()
                else:
                    # Run the wizard
                    final_df = glass_wizard.run_wizard(st.session_state['wizard_df'])
                    
                    if final_df is not None:
                        # Store the final standardized data
                        st.session_state['processed_data'] = final_df
                        st.session_state['data'] = final_df
                        
                        # Comprehensive AMR Quality Assessment
                        from utils.amr_data_quality import AMRDataQuality
                        amr_quality = AMRDataQuality()
                        
                        st.markdown("---")
                        st.markdown("### 🧬 Final AMR Data Quality Assessment")
                        amr_report = amr_quality.assess_amr_data_quality(final_df, context='glass')
                        amr_quality.display_amr_quality_report(amr_report)
                        
                        # Auto-fix if needed
                        if amr_report.get('quality_score', 0) < 80 or not amr_report.get('glass_submission_ready', False):
                            st.warning("⚠️ Data quality can be improved. Apply auto-fixes below:")
                            if st.button("🚀 Apply Comprehensive Auto-Fixes", type="primary", use_container_width=True):
                                with st.spinner("Applying comprehensive auto-fixes..."):
                                    final_df = amr_quality.comprehensive_auto_fix(final_df)
                                    st.session_state['processed_data'] = final_df
                                    st.session_state['data'] = final_df
                                    st.success("✅ Auto-fixes applied! Re-assessing quality...")
                                    st.rerun()
                        
                        # Show export option
                        st.markdown("---")
                        from utils.ui_components import ui_components
                        ui_components.section_header(
                            "Export Your GLASS-Ready Data",
                            icon="📥",
                            description="Your data is now ready for GLASS submission"
                        )
                        
                        # Export options
                        from utils.excel_exporter import ExcelExporter
                        exporter = ExcelExporter()
                        
                        st.write("### Export Your GLASS-Ready Data")
                        if amr_report.get('glass_submission_ready', False):
                            st.success("✅ Your data has been cleaned, standardized, and validated. It's ready for GLASS submission!")
                        else:
                            st.info("ℹ️ Your data has been processed. Review the quality assessment above before submission.")
                        
                        # Use the exporter's interface
                        exporter.show_export_interface(final_df, None)
                        
            except Exception as e:
                st.error(f"❌ Error in GLASS Wizard: {str(e)}")
                st.error("Please try again or contact support if the issue persists.")
                if logger:
                    logger.log_error(e, context="Error in GLASS Wizard")
        
        # WHONET Preparation Wizard Workflow
        elif st.session_state['workflow_type'] == 'health':
            # Health monitoring page (production only)
            try:
                from utils.health_endpoint import render_health_page
                render_health_page()
            except Exception as e:
                st.error(f"❌ Health monitoring not available: {str(e)}")
                st.info("Health monitoring is only available in production mode.")
        
        elif st.session_state['workflow_type'] == 'whonet':
            try:
                from utils.whonet_wizard import WHONETWizard
                from utils.file_handler import FileHandler
                
                whonet_wizard = WHONETWizard()
                file_handler = FileHandler()
                
                # Check if data is already uploaded
                if 'whonet_wizard_df' not in st.session_state or st.session_state.get('whonet_wizard_df') is None:
                    from utils.ui_components import ui_components
                    ui_components.section_header(
                        "WHONET Data Preparation Wizard",
                        icon="🔬",
                        description="Upload your AMR data file to begin the guided preparation process"
                    )
                    
                    ui_components.info_banner(
                        "📋 **What you need:** A CSV or Excel file with your AMR data (organism names, antimicrobial results, patient information, etc.)",
                        type="info"
                    )
                    
                    uploaded_df = file_handler.upload_file()
                    
                    if uploaded_df is not None:
                        st.session_state['whonet_wizard_df'] = uploaded_df
                        st.session_state['whonet_wizard_started'] = True
                        st.rerun()
                else:
                    # Run the wizard
                    final_df = whonet_wizard.run_wizard(st.session_state['whonet_wizard_df'])
                    
                    if final_df is not None:
                        # Store the final standardized data
                        st.session_state['processed_data'] = final_df
                        st.session_state['data'] = final_df
                        
                        # Comprehensive AMR Quality Assessment
                        from utils.amr_data_quality import AMRDataQuality
                        amr_quality = AMRDataQuality()
                        
                        st.markdown("---")
                        st.markdown("### 🧬 Final AMR Data Quality Assessment")
                        amr_report = amr_quality.assess_amr_data_quality(final_df, context='whonet')
                        amr_quality.display_amr_quality_report(amr_report)
                        
                        # Auto-fix if needed
                        if amr_report.get('quality_score', 0) < 80:
                            st.warning("⚠️ Data quality can be improved. Apply auto-fixes below:")
                            if st.button("🚀 Apply Comprehensive Auto-Fixes", type="primary", use_container_width=True):
                                with st.spinner("Applying comprehensive auto-fixes..."):
                                    final_df = amr_quality.comprehensive_auto_fix(final_df)
                                    st.session_state['processed_data'] = final_df
                                    st.session_state['data'] = final_df
                                    st.success("✅ Auto-fixes applied! Re-assessing quality...")
                                    st.rerun()
                        
                        # Show export option
                        st.markdown("---")
                        from utils.ui_components import ui_components
                        ui_components.section_header(
                            "Export Your WHONET-Ready Data",
                            icon="📥",
                            description="Your data is now ready for WHONET import"
                        )
                        
                        # Export options
                        from utils.excel_exporter import ExcelExporter
                        exporter = ExcelExporter()
                        
                        st.write("### Export Your WHONET-Ready Data")
                        if amr_report.get('quality_score', 0) >= 80:
                            st.success("✅ Your data has been cleaned, standardized, and validated. It's ready for WHONET import!")
                        else:
                            st.info("ℹ️ Your data has been processed. Review the quality assessment above before import.")
                        
                        # Use the exporter's interface
                        exporter.show_export_interface(final_df, None)
                        
            except Exception as e:
                st.error(f"❌ Error in WHONET Wizard: {str(e)}")
                st.error("Please try again or contact support if the issue persists.")
                if logger:
                    logger.log_error(e, context="Error in WHONET Wizard")
        
        # Enhanced reset workflow button with quick actions
        if st.session_state['workflow_selected']:
            st.markdown("---")
            from utils.ui_components import ui_components
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                if ui_components.quick_action_button(
                    "🔄 Start New Process",
                    "🔄",
                    "reset_workflow",
                    "Clear current workflow and start fresh",
                    "secondary"
                ):
                    # Use session manager for proper cleanup
                    from utils.session_manager import session_manager
                    
                    workflow_type = st.session_state.get('workflow_type')
                    
                    # Reset workflow state
                    session_manager.reset_workflow(workflow_type)
                    
                    # Reset main workflow flags
                    st.session_state['workflow_selected'] = False
                    st.session_state['workflow_type'] = None
                        
                    st.rerun()
    
    except Exception as e:
        st.error(f"❌ Application error: {str(e)}")
        st.error("Please refresh the page and try again. If the problem persists, contact support.")
        # Try to log error if logger is available
        try:
            from utils.production_logger import get_production_logger
            app_logger = get_production_logger()
            if app_logger:
                app_logger.log_error(e, context="Application error")
        except Exception:
            pass  # Ignore logging errors

if __name__ == "__main__":
    main()



