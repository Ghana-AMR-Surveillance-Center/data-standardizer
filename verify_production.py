#!/usr/bin/env python3
"""
GLASS Data Standardizer v2.0.0 - Production Verification Script
This script verifies that all components are working correctly for production deployment.
"""

import sys
import os
import importlib
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required, found {sys.version}")
        return False
    return True

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'streamlit', 'pandas', 'numpy', 'openpyxl', 'xlsxwriter', 
        'xlrd', 'plotly', 'kaleido', 'seaborn', 
        'matplotlib', 'psutil', 'scipy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def check_file_structure():
    """Check if all required files exist."""
    required_files = [
        'app.py', 'run.py', 'run_production.py', 'requirements.txt',
        'Dockerfile', 'docker-compose.yml', 'config/production.py',
        'utils/__init__.py', 'utils/file_handler.py', 'utils/file_merger.py',
        'utils/column_mapper.py', 'utils/transformer.py', 'utils/validator.py',
        'utils/amr_analytics.py', 'utils/amr_interface.py', 'utils/enhanced_amr_analytics.py',
        'utils/enhanced_amr_interface.py', 'utils/ast_detector.py', 'utils/cache_manager.py',
        'utils/user_feedback.py', 'utils/app_settings.py', 'utils/security.py',
        'utils/health_monitor.py', 'utils/production_logger.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def check_imports():
    """Check if all modules can be imported."""
    
    try:
        # Test core imports
        from utils.file_handler import FileHandler
        from utils.file_merger import FileMerger
        from utils.column_mapper import ColumnMapper
        from utils.transformer import DataTransformer
        from utils.validator import DataValidator
        from utils.amr_analytics import AMRAnalytics
        from utils.amr_interface import AMRInterface
        from utils.enhanced_amr_analytics import EnhancedAMRAnalytics
        from utils.enhanced_amr_interface import EnhancedAMRInterface
        from utils.ast_detector import ASTDataDetector
        from utils.cache_manager import streamlit_cache_dataframe
        from utils.user_feedback import user_feedback
        from utils.app_settings import app_settings
        from utils.security import security_manager
        from utils.health_monitor import health_monitor
        from utils.production_logger import initialize_production_logger
        from config.production import production_config
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def check_configuration():
    """Check if configuration is valid."""
    try:
        from config.production import production_config
        return production_config.validate_config()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def check_directories():
    """Check if required directories exist or can be created."""
    
    required_dirs = ['logs', 'data', 'config']
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/")
        else:
            try:
                dir_path.mkdir(exist_ok=True)
                print(f"✅ {dir_name}/ (created)")
            except Exception as e:
                print(f"❌ {dir_name}/ - cannot create: {e}")
                return False
    
    return True

def main():
    """Main verification function."""
    print("🏥 GLASS Data Standardizer v2.0.0 - Production Verification")
    print("=" * 60)
    
    checks = [
        check_python_version,
        check_dependencies,
        check_file_structure,
        check_imports,
        check_configuration,
        check_directories
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    if all_passed:
        print("🎉 ALL CHECKS PASSED - Production Ready!")
        print("✅ The application is ready for deployment")
    else:
        print("❌ SOME CHECKS FAILED - Please fix issues before deployment")
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
