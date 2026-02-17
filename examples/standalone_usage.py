"""
Standalone Usage Examples
Demonstrates how to use AMR Data Harmonizer modules independently
without the Streamlit interface.
"""

import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Example 1: Basic data processing pipeline
def example_basic_pipeline():
    """Basic data processing without Streamlit"""
    from utils.file_handler import FileHandler
    from utils.transformer import DataTransformer
    from utils.validator import DataValidator
    from utils.excel_exporter import ExcelExporter
    
    # Load data (standalone - not using Streamlit file uploader)
    df = pd.read_csv('data/sample_data.csv')
    
    # Initialize components
    transformer = DataTransformer()
    validator = DataValidator()
    exporter = ExcelExporter()
    
    # Process data
    cleaned_df = transformer.clean_data(df)
    validation_results = validator.validate_data(cleaned_df)
    
    # Export
    output_path = 'output/cleaned_data.xlsx'
    exporter.export_to_excel(cleaned_df, output_path)
    
    print(f"✅ Processed {len(cleaned_df)} rows")
    print(f"✅ Exported to {output_path}")
    
    return cleaned_df

# Example 2: AMR data quality assessment
def example_amr_quality_assessment():
    """AMR-specific quality assessment standalone"""
    from utils.amr_data_quality import AMRDataQuality
    
    # Load AMR data
    df = pd.read_csv('data/amr_data.csv')
    
    # Initialize AMR quality assessor
    amr_quality = AMRDataQuality()
    
    # Assess quality
    quality_report = amr_quality.assess_amr_data_quality(df, context='glass')
    
    # Print results
    print(f"Quality Score: {quality_report['quality_score']:.1f}%")
    print(f"GLASS Ready: {quality_report['glass_submission_ready']}")
    
    # Apply auto-fixes if needed
    if quality_report['quality_score'] < 80:
        print("Applying auto-fixes...")
        fixed_df = amr_quality.comprehensive_auto_fix(df)
        
        # Re-assess
        new_report = amr_quality.assess_amr_data_quality(fixed_df, context='glass')
        print(f"New Quality Score: {new_report['quality_score']:.1f}%")
        
        return fixed_df
    
    return df

# Example 3: GLASS standardization
def example_glass_standardization():
    """GLASS standardization standalone"""
    from utils.glass_standardizer import GLASSStandardizer
    
    # Load data
    df = pd.read_csv('data/amr_data.csv')
    
    # Initialize standardizer
    standardizer = GLASSStandardizer()
    
    # Standardize
    standardized_df, cleaning_report = standardizer.standardize_for_glass(df, auto_fix=True)
    
    # Print report
    print("Cleaning Report:")
    for issue in cleaning_report.get('issues_fixed', []):
        print(f"  ✅ {issue}")
    
    # Export
    standardized_df.to_csv('output/glass_ready_data.csv', index=False)
    print("✅ GLASS-ready data exported")
    
    return standardized_df

# Example 4: File merging
def example_file_merging():
    """Merge multiple files standalone"""
    from utils.file_merger import FileMerger
    
    # Load multiple files
    files = [
        'data/file1.csv',
        'data/file2.csv',
        'data/file3.csv'
    ]
    
    dataframes = [pd.read_csv(f) for f in files]
    
    # Initialize merger
    merger = FileMerger()
    
    # Merge (using internal method, not Streamlit interface)
    merged_df = merger.merge_dataframes(dataframes)
    
    print(f"✅ Merged {len(files)} files into {len(merged_df)} rows")
    
    return merged_df

# Example 5: Complete pipeline with all modules
def example_complete_pipeline():
    """Complete data processing pipeline using all modules"""
    from utils import create_standalone_pipeline
    
    # Create pipeline
    pipeline = create_standalone_pipeline()
    
    # Load data
    df = pd.read_csv('data/amr_data.csv')
    
    # Step 1: Analyze schema
    schema = pipeline['schema_analyzer'].analyze_schema(df)
    print("Schema analyzed")
    
    # Step 2: Assess quality
    quality = pipeline['quality_assessor'].assess_data_quality(df)
    print(f"Data quality score: {quality['score']:.1%}")
    
    # Step 3: AMR-specific assessment
    amr_report = pipeline['amr_quality'].assess_amr_data_quality(df)
    print(f"AMR quality score: {amr_report['quality_score']:.1f}%")
    
    # Step 4: Standardize for GLASS
    if amr_report['quality_score'] < 80:
        df = pipeline['amr_quality'].comprehensive_auto_fix(df)
        print("Applied auto-fixes")
    
    standardized_df, _ = pipeline['glass_standardizer'].standardize_for_glass(df)
    
    # Step 5: Validate
    validation = pipeline['validator'].validate_data(standardized_df)
    print(f"Validation: {len(validation['errors'])} errors, {len(validation['warnings'])} warnings")
    
    # Step 6: Export
    pipeline['excel_exporter'].export_to_excel(standardized_df, 'output/final_data.xlsx')
    print("✅ Complete pipeline finished")
    
    return standardized_df

# Example 6: AMR analytics standalone
def example_amr_analytics():
    """AMR analytics without Streamlit interface"""
    from utils.amr_analytics import AMRAnalytics
    
    # Load data
    df = pd.read_csv('data/amr_data.csv')
    
    # Initialize analytics
    analytics = AMRAnalytics()
    
    # Calculate resistance rates
    resistance_rates = analytics.calculate_resistance_rates_enhanced(df)
    
    # Create visualizations (returns figure objects, not Streamlit components)
    antibiogram = analytics.create_professional_antibiogram(df)
    org_dist = analytics.create_organism_distribution_chart(df)
    
    # Export charts
    if antibiogram:
        antibiogram.write_image('output/antibiogram.png')
        print("✅ Antibiogram exported")
    
    if org_dist:
        org_dist.write_image('output/organism_distribution.png')
        print("✅ Organism distribution chart exported")
    
    # Export resistance rates
    resistance_rates.to_csv('output/resistance_rates.csv', index=False)
    print("✅ Resistance rates exported")
    
    return resistance_rates

if __name__ == "__main__":
    print("AMR Data Harmonizer - Standalone Usage Examples")
    print("=" * 60)
    
    # Run examples (uncomment the one you want to test)
    # example_basic_pipeline()
    # example_amr_quality_assessment()
    # example_glass_standardization()
    # example_file_merging()
    # example_complete_pipeline()
    # example_amr_analytics()
    
    print("\n✅ Examples ready. Uncomment the example you want to run.")

