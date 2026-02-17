# 🏥 AMR Data Harmonizer - Deployment Package

## Quick Start

### 1. Setup
```bash
python setup.py
```

### 2. Run
```bash
python run.py
```

### 3. Access
Open your browser to: http://localhost:8501

## System Requirements

- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 1GB free space
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)

## Features

- **Single File Processing**: Upload, analyze, transform, and export individual files
- **Multiple File Merging**: Intelligent merging of multiple Excel/CSV files
- **Smart Column Mapping**: AI-powered column matching and mapping
- **Data Transformation**: Comprehensive data cleaning and standardization
- **Quality Assessment**: Advanced data quality metrics and validation
- **Multi-format Export**: Export to CSV, Excel, JSON, XML formats

## Production Features

- **Error Handling**: Comprehensive error logging and recovery
- **Performance Monitoring**: Real-time performance metrics and optimization
- **Data Validation**: Multi-level data validation and quality checks
- **Memory Optimization**: Automatic DataFrame optimization
- **Configuration Management**: Centralized settings and customization

## Troubleshooting

### Common Issues

1. **Python Not Found**
   - Install Python 3.8+ from https://python.org
   - Ensure Python is in PATH

2. **Dependencies Not Installing**
   - Check internet connection
   - Try: `pip install --upgrade pip`
   - Run setup.py again

3. **Port Already in Use**
   - Kill existing processes: `taskkill /f /im python.exe`
   - Or use different port: `streamlit run app.py --server.port 8502`

4. **Virtual Environment Issues**
   - Delete .venv folder and run setup.py again
   - Ensure you have write permissions

### Getting Help

- Check the error messages in the terminal
- Review the application logs
- Ensure all system requirements are met
- Try running as administrator if on Windows

## File Structure

```
data-standardizer/
├── app.py                 # Main application
├── run.py                 # Production launcher
├── setup.py              # Setup script
├── requirements.txt      # Dependencies
├── start_app.bat         # Windows launcher
├── README.md             # This file
├── utils/                # Utility modules
│   ├── __init__.py
│   ├── app_config.py     # Configuration management
│   ├── column_mapper.py  # Column mapping logic
│   ├── data_filter.py    # Data filtering
│   ├── data_profiler.py  # Data profiling
│   ├── data_quality.py   # Data quality assessment
│   ├── error_handler.py  # Error handling
│   ├── excel_exporter.py # Export functionality
│   ├── file_handler.py   # File processing
│   ├── file_merger.py    # File merging
│   ├── helpers.py        # Helper functions
│   ├── logger.py         # Logging system
│   ├── performance_monitor.py # Performance monitoring
│   ├── schema_analyzer.py # Schema analysis
│   ├── transformer.py    # Data transformation
│   ├── validation.py     # Data validation
│   └── validator.py      # Validation logic
└── .venv/               # Virtual environment (created by setup)
```

## Support

For technical support or issues, check the troubleshooting section above or review the application logs.

---

**Version**: 2.0.0  
**Last Updated**: 2024  
**Compatibility**: Python 3.8+, Windows 10+, macOS 10.14+, Linux Ubuntu 18.04+
