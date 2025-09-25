#!/usr/bin/env python3
"""
Dependency checker for GLASS Data Standardizer
Checks if all required libraries are installed and working properly.
"""

import sys
import importlib
from typing import List, Tuple

def check_library(library_name: str, import_name: str = None) -> Tuple[bool, str]:
    """
    Check if a library is installed and can be imported.
    
    Args:
        library_name: Name of the library for display
        import_name: Name to use for import (if different from library_name)
    
    Returns:
        Tuple of (success, message)
    """
    if import_name is None:
        import_name = library_name
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'Unknown version')
        return True, f"✅ {library_name} ({version})"
    except ImportError as e:
        return False, f"❌ {library_name} - Not installed: {str(e)}"
    except Exception as e:
        return False, f"⚠️ {library_name} - Error: {str(e)}"

def main():
    """Main dependency check function."""
    print("GLASS Data Standardizer - Dependency Check")
    print("=" * 50)
    
    # List of required libraries
    required_libraries = [
        ("Streamlit", "streamlit"),
        ("Pandas", "pandas"),
        ("NumPy", "numpy"),
        ("OpenPyXL", "openpyxl"),
        ("Pathlib", "pathlib"),
        ("JSON", "json"),
        ("Regular Expressions", "re"),
        ("Typing", "typing"),
        ("IO", "io"),
    ]
    
    # Check each library
    all_good = True
    for lib_name, import_name in required_libraries:
        success, message = check_library(lib_name, import_name)
        print(message)
        if not success:
            all_good = False
    
    print("\n" + "=" * 50)
    
    # Test importing custom modules
    print("\nChecking custom modules:")
    custom_modules = [
        ("File Handler", "utils.file_handler"),
        ("Schema Analyzer", "utils.schema_analyzer"),
        ("Column Mapper", "utils.column_mapper"),
        ("Data Filter", "utils.data_filter"),
        ("Data Transformer", "utils.transformer"),
        ("Data Validator", "utils.validator"),
        ("Excel Exporter", "utils.excel_exporter"),
        ("File Merger", "utils.file_merger"),
        ("Helpers", "utils.helpers"),
    ]
    
    for module_name, import_name in custom_modules:
        success, message = check_library(module_name, import_name)
        print(message)
        if not success:
            all_good = False
    
    print("\n" + "=" * 50)
    
    # Test basic functionality
    print("\nTesting basic functionality:")
    
    try:
        import pandas as pd
        import numpy as np
        
        # Test DataFrame creation
        test_df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        print("✅ Pandas DataFrame creation works")
        
        # Test NumPy operations
        test_array = np.array([1, 2, 3])
        print("✅ NumPy array operations work")
        
        # Test Excel writing capability
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            test_df.to_excel(writer, index=False)
        print("✅ Excel export functionality works")
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {str(e)}")
        all_good = False
    
    print("\n" + "=" * 50)
    
    # Final result
    if all_good:
        print("🎉 All dependencies are installed and working properly!")
        print("✅ The GLASS Data Standardizer should run without issues.")
    else:
        print("⚠️ Some dependencies are missing or not working properly.")
        print("❌ Please install missing dependencies before running the application.")
        
        print("\nTo install missing dependencies, try:")
        print("pip install streamlit pandas numpy openpyxl")
    
    print(f"\nPython version: {sys.version}")
    print(f"Python executable: {sys.executable}")

if __name__ == "__main__":
    main()
