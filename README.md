# Data Standardizer - Medical Data Standardization Platform

A comprehensive Streamlit application for standardizing medical data files with intelligent column mapping, filtering, and validation capabilities.

## Features

- **File Upload & Schema Analysis**: Support for CSV/Excel files with automatic schema detection
- **Intelligent Column Mapping**: Smart mapping of uploaded data columns to target schema
- **Advanced Filtering**: Comprehensive filtering options with regex support
- **Bulk Transformations**: Case conversion, trimming, and data standardization
- **Validation Engine**: Real-time data validation with error reporting
- **Excel Export**: High-quality Excel exports with professional formatting

## Installation

1. Clone or download this project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Upload your CSV or Excel file
2. Review the automatic schema analysis
3. Map columns using the intelligent mapping wizard
4. Apply filters and transformations as needed
5. Validate your data and review any issues
6. Export the standardized data to Excel

## Project Structure

```
data-standardizer/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── file_handler.py    # File upload and processing
│   ├── schema_analyzer.py # Schema detection and analysis
│   ├── column_mapper.py   # Intelligent column mapping
│   ├── data_filter.py     # Data filtering operations
│   ├── transformer.py     # Data transformation functions
│   ├── validator.py       # Data validation engine
│   └── excel_exporter.py  # Excel export functionality
└── README.md
```

## Requirements

- Python 3.8+
- Streamlit 1.28.0+
- See requirements.txt for complete dependency list
