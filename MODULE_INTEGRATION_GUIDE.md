# Module Integration and Standalone Usage Guide

## Overview

The GLASS Data Standardizer is designed with modular architecture, allowing each component to be used:
1. **Integrated**: As part of the main Streamlit application
2. **Independently**: As standalone Python modules in scripts or other applications

## Module Categories

### 1. Core Data Processing Modules
- `FileHandler`: File upload and reading
- `FileMerger`: Merging multiple files
- `SchemaAnalyzer`: Analyzing data structure
- `ColumnMapper`: Column mapping and renaming
- `DataTransformer`: Data cleaning and transformation
- `DataValidator`: Data validation
- `ExcelExporter`: Export to various formats

### 2. Data Quality Modules
- `DataQualityAssessor`: General data quality assessment
- `DataProfiler`: Data profiling and statistics
- `AMRDataQuality`: AMR-specific quality assessment
- `EnhancedQualityReporter`: Enhanced quality reporting

### 3. AMR Analysis Modules
- `AMRAnalytics`: Basic AMR analytics
- `EnhancedAMRAnalytics`: Enhanced AMR analytics with statistics
- `AMRInterface`: Streamlit interface for AMR analysis
- `EnhancedAMRInterface`: Enhanced Streamlit interface
- `ASTDataDetector`: AST data type detection

### 4. Standardization Modules
- `GLASSStandardizer`: GLASS format standardization
- `WHONETStandardizer`: WHONET format standardization
- `GLASSWizard`: Step-by-step GLASS preparation wizard
- `WHONETWizard`: Step-by-step WHONET preparation wizard

### 5. UI and User Experience Modules
- `UIComponents`: Reusable UI components
- `UIValidator`: UI validation and user feedback
- `UserFeedback`: User feedback system

### 6. System and Configuration Modules
- `AppConfig`: Application configuration
- `AppSettings`: Application settings management
- `CacheManager`: Caching system
- `SessionManager`: Session state management
- `ErrorHandler`: Error handling
- `ProductionLogger`: Production logging

## Integrated Usage (Streamlit App)

### In the Main Application

All modules are automatically integrated in `app.py`:

```python
from utils.file_handler import FileHandler
from utils.transformer import DataTransformer
# ... other imports

# Initialize in main()
file_handler = FileHandler()
transformer = DataTransformer()
# ... use in workflows
```

### Workflow Integration

1. **Single File Workflow**: Uses FileHandler → SchemaAnalyzer → ColumnMapper → DataTransformer → DataValidator → ExcelExporter
2. **Multiple Files Workflow**: Uses FileMerger → DataTransformer → DataValidator → ExcelExporter
3. **AMR Analytics Workflow**: Uses AMRInterface/EnhancedAMRInterface → AMRAnalytics
4. **GLASS Wizard**: Uses GLASSWizard → GLASSStandardizer → AMRDataQuality
5. **WHONET Wizard**: Uses WHONETWizard → WHONETStandardizer → AMRDataQuality

## Standalone Usage

### Basic Standalone Usage

```python
import pandas as pd
from utils.transformer import DataTransformer
from utils.validator import DataValidator

# Load data
df = pd.read_csv('data.csv')

# Initialize modules
transformer = DataTransformer()
validator = DataValidator()

# Use modules
cleaned_df = transformer.clean_data(df)
validation_results = validator.validate_data(cleaned_df)
```

### Complete Pipeline Standalone

```python
from utils import create_standalone_pipeline
import pandas as pd

# Create all components at once
pipeline = create_standalone_pipeline()

# Load data
df = pd.read_csv('data.csv')

# Use components
schema = pipeline['schema_analyzer'].analyze_schema(df)
quality = pipeline['quality_assessor'].assess_data_quality(df)
cleaned_df = pipeline['transformer'].clean_data(df)
```

### AMR Quality Assessment Standalone

```python
from utils.amr_data_quality import AMRDataQuality
import pandas as pd

df = pd.read_csv('amr_data.csv')
amr_quality = AMRDataQuality()

# Assess quality
report = amr_quality.assess_amr_data_quality(df, context='glass')

# Apply fixes if needed
if report['quality_score'] < 80:
    fixed_df = amr_quality.comprehensive_auto_fix(df)
```

### GLASS Standardization Standalone

```python
from utils.glass_standardizer import GLASSStandardizer
import pandas as pd

df = pd.read_csv('amr_data.csv')
standardizer = GLASSStandardizer()

# Standardize
standardized_df, report = standardizer.standardize_for_glass(df, auto_fix=True)

# Export
standardized_df.to_csv('glass_ready.csv', index=False)
```

## Module Dependencies

### Minimal Dependencies
Most modules have minimal dependencies and can work independently:
- Core modules only depend on `pandas`, `numpy`
- UI modules depend on `streamlit` (only needed for Streamlit apps)
- AMR modules depend on `plotly` for visualizations

### Optional Dependencies
- `streamlit`: Only needed for UI components
- `plotly`: Only needed for visualizations
- `kaleido`: Only needed for exporting charts

## Error Handling for Independent Use

### Checking Module Availability

```python
from utils import check_module_availability

status = check_module_availability()
print(status)
# {'core_processing': True, 'data_quality': True, ...}
```

### Handling Missing Dependencies

```python
try:
    from utils.amr_analytics import AMRAnalytics
    analytics = AMRAnalytics()
except ImportError as e:
    print(f"AMR Analytics not available: {e}")
    # Use alternative or skip
```

## Best Practices

### 1. Initialize Once, Reuse
```python
# Good: Initialize once
transformer = DataTransformer()
df1_cleaned = transformer.clean_data(df1)
df2_cleaned = transformer.clean_data(df2)

# Avoid: Re-initializing
df1_cleaned = DataTransformer().clean_data(df1)
df2_cleaned = DataTransformer().clean_data(df2)
```

### 2. Handle Errors Gracefully
```python
try:
    from utils.glass_standardizer import GLASSStandardizer
    standardizer = GLASSStandardizer()
    result = standardizer.standardize_for_glass(df)
except Exception as e:
    print(f"Error: {e}")
    # Fallback or error handling
```

### 3. Use Appropriate Context
```python
# For GLASS submission
amr_quality.assess_amr_data_quality(df, context='glass')

# For WHONET import
amr_quality.assess_amr_data_quality(df, context='whonet')

# General assessment
amr_quality.assess_amr_data_quality(df, context='general')
```

## Integration Points

### Adding New Modules

1. Create module in `utils/` directory
2. Add to `utils/__init__.py` exports
3. Import in `app.py` if needed for workflows
4. Add standalone usage example in `examples/standalone_usage.py`

### Extending Workflows

1. Import required modules in workflow section
2. Initialize modules as needed
3. Chain operations logically
4. Handle errors appropriately
5. Update session state if needed

## Testing Module Independence

Run the standalone examples:

```bash
python examples/standalone_usage.py
```

Or test individual modules:

```python
from utils import check_module_availability
status = check_module_availability()
assert all(status.values()), "Some modules not available"
```

## Common Use Cases

### Use Case 1: Batch Processing Script
```python
from utils.glass_standardizer import GLASSStandardizer
import pandas as pd
import glob

standardizer = GLASSStandardizer()
files = glob.glob('data/*.csv')

for file in files:
    df = pd.read_csv(file)
    standardized, _ = standardizer.standardize_for_glass(df)
    standardized.to_csv(f'output/{file.name}', index=False)
```

### Use Case 2: Quality Check Script
```python
from utils.amr_data_quality import AMRDataQuality
import pandas as pd

amr_quality = AMRDataQuality()
df = pd.read_csv('data.csv')

report = amr_quality.assess_amr_data_quality(df)
if not report['glass_submission_ready']:
    print("Issues found:")
    for issue in report['issues']:
        print(f"  - {issue['message']}")
```

### Use Case 3: Data Transformation API
```python
from utils.transformer import DataTransformer
from flask import Flask, request, jsonify

app = Flask(__name__)
transformer = DataTransformer()

@app.route('/transform', methods=['POST'])
def transform_data():
    df = pd.DataFrame(request.json)
    cleaned = transformer.clean_data(df)
    return jsonify(cleaned.to_dict('records'))
```

## Summary

- ✅ All modules can be used independently
- ✅ All modules are integrated in the main app
- ✅ Minimal dependencies for core functionality
- ✅ Clear separation of concerns
- ✅ Easy to extend and customize
- ✅ Comprehensive error handling
- ✅ Well-documented usage patterns

For more examples, see `examples/standalone_usage.py`.

