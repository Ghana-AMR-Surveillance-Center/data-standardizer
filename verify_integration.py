"""
Integration Verification Script
Verifies that all modules can be imported and used both integrated and independently.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    
    modules_to_test = [
        ('utils.file_handler', 'FileHandler'),
        ('utils.schema_analyzer', 'SchemaAnalyzer'),
        ('utils.column_mapper', 'ColumnMapper'),
        ('utils.transformer', 'DataTransformer'),
        ('utils.validator', 'DataValidator'),
        ('utils.excel_exporter', 'ExcelExporter'),
        ('utils.file_merger', 'FileMerger'),
        ('utils.data_quality', 'DataQualityAssessor'),
        ('utils.data_profiler', 'DataProfiler'),
        ('utils.amr_data_quality', 'AMRDataQuality'),
        ('utils.glass_standardizer', 'GLASSStandardizer'),
        ('utils.whonet_standardizer', 'WHONETStandardizer'),
        ('utils.amr_analytics', 'AMRAnalytics'),
    ]
    
    results = {}
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            # Try to instantiate
            instance = cls()
            results[class_name] = {'import': True, 'instantiate': True, 'error': None}
            print(f"  [OK] {class_name}: Import and instantiation successful")
        except ImportError as e:
            results[class_name] = {'import': False, 'instantiate': False, 'error': str(e)}
            print(f"  [FAIL] {class_name}: Import failed - {str(e)}")
        except Exception as e:
            results[class_name] = {'import': True, 'instantiate': False, 'error': str(e)}
            print(f"  [WARN] {class_name}: Import successful but instantiation failed - {str(e)}")
    
    return results

def test_standalone_usage():
    """Test standalone usage of key modules"""
    print("\nTesting standalone usage...")
    
    try:
        from utils.file_handler import FileHandler
        file_handler = FileHandler()
        
        # Test standalone method exists
        if hasattr(file_handler, 'read_file'):
            print("  [OK] FileHandler.read_file() available for standalone use")
        else:
            print("  [FAIL] FileHandler.read_file() not found")
        
        if hasattr(file_handler, 'read_file_from_bytes'):
            print("  [OK] FileHandler.read_file_from_bytes() available for standalone use")
        else:
            print("  [FAIL] FileHandler.read_file_from_bytes() not found")
            
    except Exception as e:
        print(f"  [FAIL] Standalone usage test failed: {str(e)}")
    
    try:
        from utils.amr_data_quality import AMRDataQuality
        amr_quality = AMRDataQuality()
        
        if hasattr(amr_quality, 'comprehensive_auto_fix'):
            print("  [OK] AMRDataQuality.comprehensive_auto_fix() available")
        else:
            print("  [FAIL] AMRDataQuality.comprehensive_auto_fix() not found")
            
    except Exception as e:
        print(f"  [FAIL] AMR quality standalone test failed: {str(e)}")

def test_integration():
    """Test that modules work together"""
    print("\nTesting module integration...")
    
    try:
        from utils import create_standalone_pipeline
        pipeline = create_standalone_pipeline()
        
        print(f"  [OK] Created standalone pipeline with {len(pipeline)} components")
        print(f"     Components: {', '.join(pipeline.keys())}")
        
    except Exception as e:
        print(f"  [FAIL] Integration test failed: {str(e)}")

def main():
    print("=" * 60)
    print("GLASS Data Standardizer - Integration Verification")
    print("=" * 60)
    
    # Test imports
    results = test_imports()
    
    # Test standalone usage
    test_standalone_usage()
    
    # Test integration
    test_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    total = len(results)
    successful_imports = sum(1 for r in results.values() if r['import'])
    successful_instantiations = sum(1 for r in results.values() if r['instantiate'])
    
    print(f"Total modules tested: {total}")
    print(f"Successful imports: {successful_imports}/{total}")
    print(f"Successful instantiations: {successful_instantiations}/{total}")
    
    if successful_imports == total and successful_instantiations == total:
        print("\n[SUCCESS] All modules are properly integrated and can be used independently!")
        return 0
    else:
        print("\n[WARNING] Some modules have issues. Check errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

