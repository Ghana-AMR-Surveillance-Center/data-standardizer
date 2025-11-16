# Module Integration and Standalone Usage Summary

## ✅ Integration Status

All modules are now fully integrated into the main application workflows and can also be used independently.

## Module Architecture

### 1. **Core Processing Modules** (Standalone + Integrated)
- ✅ `FileHandler`: File reading (standalone) and upload (Streamlit)
- ✅ `FileMerger`: Merges multiple files
- ✅ `SchemaAnalyzer`: Analyzes data structure
- ✅ `ColumnMapper`: Maps columns to standard names
- ✅ `DataTransformer`: Cleans and transforms data
- ✅ `DataValidator`: Validates data quality
- ✅ `ExcelExporter`: Exports to multiple formats

### 2. **Data Quality Modules** (Standalone + Integrated)
- ✅ `DataQualityAssessor`: General quality assessment
- ✅ `DataProfiler`: Data profiling
- ✅ `AMRDataQuality`: AMR-specific quality with auto-fix
- ✅ `EnhancedQualityReporter`: Enhanced reporting

### 3. **AMR Analysis Modules** (Standalone + Integrated)
- ✅ `AMRAnalytics`: Basic AMR analytics
- ✅ `EnhancedAMRAnalytics`: Enhanced analytics with statistics
- ✅ `ASTDataDetector`: Detects AST data types

### 4. **Standardization Modules** (Standalone + Integrated)
- ✅ `GLASSStandardizer`: GLASS format standardization
- ✅ `WHONETStandardizer`: WHONET format standardization
- ✅ `GLASSWizard`: Step-by-step GLASS wizard (Streamlit)
- ✅ `WHONETWizard`: Step-by-step WHONET wizard (Streamlit)

### 5. **UI Components** (Streamlit Only)
- ✅ `UIComponents`: Reusable UI components
- ✅ `UIValidator`: UI validation and feedback
- ✅ `UserFeedback`: User feedback system

## Integration Points

### Main Application (`app.py`)
All modules are imported and initialized in the main application:

```python
# All imports at top level
from utils.file_handler import FileHandler
from utils.transformer import DataTransformer
# ... etc

# Initialized in main() function
file_handler = FileHandler()
transformer = DataTransformer()
# ... etc
```

### Workflow Integration

1. **Single File Workflow**
   - FileHandler → SchemaAnalyzer → ColumnMapper → DataTransformer → DataValidator → ExcelExporter
   - AMRDataQuality integrated for AMR data detection

2. **Multiple Files Workflow**
   - FileMerger → DataTransformer → DataValidator → ExcelExporter
   - AMRDataQuality integrated for merged data

3. **AMR Analytics Workflow**
   - AMRInterface/EnhancedAMRInterface → AMRAnalytics/EnhancedAMRAnalytics

4. **GLASS Wizard**
   - GLASSWizard → GLASSStandardizer → AMRDataQuality

5. **WHONET Wizard**
   - WHONETWizard → WHONETStandardizer → AMRDataQuality

## Standalone Usage

### Basic Standalone Example

```python
import pandas as pd
from utils.file_handler import FileHandler
from utils.transformer import DataTransformer

# Load data
file_handler = FileHandler()
df = file_handler.read_file('data.csv')  # Standalone method

# Process
transformer = DataTransformer()
cleaned_df = transformer.clean_data(df)
```

### Complete Pipeline Standalone

```python
from utils import create_standalone_pipeline
import pandas as pd

# Create all components
pipeline = create_standalone_pipeline()

# Use components
df = pd.read_csv('data.csv')
schema = pipeline['schema_analyzer'].analyze_schema(df)
quality = pipeline['quality_assessor'].assess_data_quality(df)
```

### AMR Quality Standalone

```python
from utils.amr_data_quality import AMRDataQuality
import pandas as pd

df = pd.read_csv('amr_data.csv')
amr_quality = AMRDataQuality()

# Assess
report = amr_quality.assess_amr_data_quality(df)

# Auto-fix
if report['quality_score'] < 80:
    fixed_df = amr_quality.comprehensive_auto_fix(df)
```

## Key Features

### ✅ Dual Mode Support
- **Integrated**: Uses Streamlit UI components
- **Standalone**: Works without Streamlit

### ✅ Optional Dependencies
- Streamlit: Only required for UI components
- Plotly: Only required for visualizations
- Other dependencies: Gracefully handled if missing

### ✅ Error Handling
- Comprehensive error messages
- Fallback options when dependencies missing
- Clear guidance for users

### ✅ Module Independence
- Each module can be imported and used separately
- Minimal cross-dependencies
- Clear separation of concerns

## Testing

### Check Module Availability

```python
from utils import check_module_availability

status = check_module_availability()
# Returns: {'core_processing': True, 'data_quality': True, ...}
```

### Test Standalone Usage

See `examples/standalone_usage.py` for complete examples.

## Documentation

- **Module Integration Guide**: `MODULE_INTEGRATION_GUIDE.md`
- **Standalone Examples**: `examples/standalone_usage.py`
- **Module Exports**: `utils/__init__.py`

## Summary

✅ All modules integrated into workflows
✅ All modules can be used independently
✅ Proper error handling and fallbacks
✅ Clear documentation and examples
✅ Dual mode support (Streamlit + standalone)

