"""
AMR Data Harmonizer - Utils Package
Comprehensive data standardization and AMR analysis utilities.

This package provides modular components that can be used:
1. Integrated: As part of the main Streamlit application
2. Independently: As standalone Python modules in scripts or other applications

Usage Examples:

# Integrated (in Streamlit app):
from utils.file_handler import FileHandler
file_handler = FileHandler()
df = file_handler.upload_file()

# Independent (in Python script):
from utils.file_handler import FileHandler
import pandas as pd

file_handler = FileHandler()
# For standalone use, read file directly
df = pd.read_csv('data.csv')
# Then use other utilities
from utils.transformer import DataTransformer
transformer = DataTransformer()
cleaned_df = transformer.clean_data(df)
"""

# Core Data Processing Modules
from .file_handler import FileHandler
from .file_merger import FileMerger
from .schema_analyzer import SchemaAnalyzer
from .column_mapper import ColumnMapper
from .transformer import DataTransformer
from .validator import DataValidator
from .excel_exporter import ExcelExporter

# Data Quality Modules
from .data_quality import DataQualityAssessor
from .data_profiler import DataProfiler
from .amr_data_quality import AMRDataQuality
from .enhanced_quality_reporter import EnhancedQualityReporter

# AMR Analysis Modules
from .amr_analytics import AMRAnalytics
from .enhanced_amr_analytics import EnhancedAMRAnalytics
from .amr_interface import AMRInterface
from .enhanced_amr_interface import EnhancedAMRInterface
from .ast_detector import ASTDataDetector

# Standardization Modules
from .glass_standardizer import GLASSStandardizer
from .whonet_standardizer import WHONETStandardizer
from .glass_wizard import GLASSWizard
from .whonet_wizard import WHONETWizard

# UI and User Experience Modules
from .ui_components import UIComponents, ui_components
from .ui_validator import UIValidator, ui_validator
from .user_feedback import UserFeedback, user_feedback

# System and Configuration Modules
from .app_config import app_config
from .app_settings import AppSettings, app_settings
from .cache_manager import CacheManager, clear_all_caches
from .session_manager import SessionManager, session_manager
from .error_handler import ErrorHandler, error_handler
from .logger import log_streamlit_action
from .production_logger import ProductionLogger, initialize_production_logger, get_production_logger

# Performance and Monitoring
try:
    from .performance_monitor import PerformanceMonitor, performance_monitor
except ImportError:
    PerformanceMonitor = None
    performance_monitor = None

try:
    from .health_monitor import HealthMonitor, health_monitor
except ImportError:
    HealthMonitor = None
    health_monitor = None

try:
    from .retry_handler import RetryHandler, retry_handler
except ImportError:
    RetryHandler = None
    retry_handler = None

# Security
from .security import SecurityManager, security_manager

# Helper utilities
from .helpers import *
from .age_transformer import AgeTransformer

# Version and metadata
__version__ = "2.0.0"
__author__ = "AMR Data Harmonizer Team"
__description__ = "Comprehensive data standardization and AMR analysis utilities"

# Module availability check
def check_module_availability():
    """
    Check if all required modules are available.
    
    Returns:
        dict: Status of each module category
    """
    status = {
        'core_processing': True,
        'data_quality': True,
        'amr_analysis': True,
        'standardization': True,
        'ui_components': True,
        'system': True
    }
    
    try:
        # Test core imports
        FileHandler()
        FileMerger()
        SchemaAnalyzer()
    except Exception:
        status['core_processing'] = False
    
    try:
        DataQualityAssessor()
        AMRDataQuality()
    except Exception:
        status['data_quality'] = False
    
    try:
        AMRAnalytics()
        ASTDataDetector()
    except Exception:
        status['amr_analysis'] = False
    
    try:
        GLASSStandardizer()
        WHONETStandardizer()
    except Exception:
        status['standardization'] = False
    
    return status

# Convenience function for standalone usage
def create_standalone_pipeline():
    """
    Create a complete data processing pipeline for standalone use.
    
    Returns:
        dict: Dictionary of initialized components ready for use
    """
    return {
        'file_handler': FileHandler(),
        'schema_analyzer': SchemaAnalyzer(),
        'column_mapper': ColumnMapper(),
        'transformer': DataTransformer(),
        'validator': DataValidator(),
        'excel_exporter': ExcelExporter(),
        'quality_assessor': DataQualityAssessor(),
        'amr_quality': AMRDataQuality(),
        'glass_standardizer': GLASSStandardizer(),
        'whonet_standardizer': WHONETStandardizer()
    }

__all__ = [
    # Core modules
    'FileHandler',
    'FileMerger',
    'SchemaAnalyzer',
    'ColumnMapper',
    'DataTransformer',
    'DataValidator',
    'ExcelExporter',
    
    # Data quality
    'DataQualityAssessor',
    'DataProfiler',
    'AMRDataQuality',
    'EnhancedQualityReporter',
    
    # AMR analysis
    'AMRAnalytics',
    'EnhancedAMRAnalytics',
    'AMRInterface',
    'EnhancedAMRInterface',
    'ASTDataDetector',
    
    # Standardization
    'GLASSStandardizer',
    'WHONETStandardizer',
    'GLASSWizard',
    'WHONETWizard',
    
    # UI components
    'UIComponents',
    'ui_components',
    'UIValidator',
    'ui_validator',
    'UserFeedback',
    'user_feedback',
    
    # System
    'app_config',
    'AppSettings',
    'app_settings',
    'CacheManager',
    'clear_all_caches',
    'SessionManager',
    'session_manager',
    'ErrorHandler',
    'error_handler',
    'log_streamlit_action',
    'ProductionLogger',
    'initialize_production_logger',
    'get_production_logger',
    
    # Performance
    'PerformanceMonitor',
    'performance_monitor',
    'HealthMonitor',
    'health_monitor',
    'RetryHandler',
    'retry_handler',
    
    # Security
    'SecurityManager',
    'security_manager',
    
    # Utilities
    'AgeTransformer',
    
    # Functions
    'check_module_availability',
    'create_standalone_pipeline',
    
    # Metadata
    '__version__',
    '__author__',
    '__description__'
]
