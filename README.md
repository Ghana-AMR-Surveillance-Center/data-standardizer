# 🏥 GLASS Data Standardizer

**Advanced Data Processing & Standardization Platform**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🚀 Quick Start

### Option 1: Automatic Setup (Recommended)
```bash
# Windows
start.bat

# Linux/macOS
python setup.py && python run.py
```

### Option 2: Manual Setup
```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
python run.py
```

### Option 3: Direct Run
```bash
python -m streamlit run app.py --server.port 8501
```

## 📋 System Requirements

- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 1GB free space
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)

## ✨ Features

### Core Functionality
- **📁 Single File Processing**: Upload, analyze, transform, and export individual files
- **📊 Multiple File Merging**: Intelligent merging of multiple Excel/CSV files
- **🔗 Smart Column Mapping**: AI-powered column matching and mapping
- **🔄 Data Transformation**: Comprehensive data cleaning and standardization
- **📈 Quality Assessment**: Advanced data quality metrics and validation
- **📤 Multi-format Export**: Export to CSV, Excel, JSON, XML formats

### Production Features
- **🛡️ Error Handling**: Comprehensive error logging and recovery
- **📊 Performance Monitoring**: Real-time performance metrics and optimization
- **✅ Data Validation**: Multi-level data validation and quality checks
- **💾 Memory Optimization**: Automatic DataFrame optimization
- **⚙️ Configuration Management**: Centralized settings and customization

## 🏗️ Architecture

```
data-standardizer/
├── app.py                 # Main Streamlit application
├── run.py                 # Production launcher
├── setup.py              # Environment setup script
├── start.bat             # Windows launcher
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── .gitignore           # Git ignore rules
├── utils/                # Core utility modules
│   ├── app_config.py     # Configuration management
│   ├── column_mapper.py  # Intelligent column mapping
│   ├── data_filter.py    # Data filtering logic
│   ├── data_profiler.py  # Data profiling and analysis
│   ├── data_quality.py   # Data quality assessment
│   ├── error_handler.py  # Error handling system
│   ├── excel_exporter.py # Multi-format export
│   ├── file_handler.py   # File processing
│   ├── file_merger.py    # File merging logic
│   ├── helpers.py        # Helper functions
│   ├── logger.py         # Logging system
│   ├── performance_monitor.py # Performance monitoring
│   ├── schema_analyzer.py # Schema analysis
│   ├── transformer.py    # Data transformation
│   ├── validation.py     # Data validation
│   └── validator.py      # Validation logic
└── deployment/           # Deployment documentation
    └── README.md         # Deployment guide
```

## 🔧 Usage

### Single File Workflow
1. **Upload**: Select and upload your data file (CSV, Excel)
2. **Analyze**: Review data structure and quality metrics
3. **Map**: Configure column mappings to target schema
4. **Transform**: Apply data cleaning and standardization
5. **Validate**: Verify data quality and completeness
6. **Export**: Download processed data in your preferred format

### Multiple File Workflow
1. **Upload**: Select multiple files for merging
2. **Validate**: Review file structures and compatibility
3. **Map**: Configure column mappings between files
4. **Merge**: Combine files with intelligent data handling
5. **Review**: Analyze merge statistics and data quality
6. **Export**: Download merged dataset

## 🛠️ Configuration

The application uses a centralized configuration system:

- **App Settings**: File size limits, memory usage, processing options
- **UI Settings**: Theme, layout, display preferences
- **Data Processing**: Chunk sizes, optimization settings
- **Merging**: Similarity thresholds, mapping preferences
- **Export**: Default formats, compression options

## 📊 Data Quality Metrics

- **Completeness**: Percentage of non-null values
- **Consistency**: Data format and value consistency
- **Accuracy**: Data accuracy validation
- **Validity**: Data validity checks
- **Uniqueness**: Duplicate detection and analysis

## 🔍 Troubleshooting

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

## 📈 Performance

- **Memory Optimization**: Automatic DataFrame optimization
- **Chunked Processing**: Large file handling
- **Caching**: Intelligent data caching
- **Monitoring**: Real-time performance metrics

## 🔒 Security

- **Input Validation**: All inputs are validated
- **File Upload Limits**: Configurable file size restrictions
- **Error Information**: Controlled error disclosure
- **Memory Management**: Automatic cleanup

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For technical support or issues:
1. Check the troubleshooting section
2. Review the application logs
3. Ensure system requirements are met
4. Check the deployment guide

---

**Version**: 2.0.0  
**Last Updated**: 2024  
**Compatibility**: Python 3.8+, Windows 10+, macOS 10.14+, Linux Ubuntu 18.04+

**Made with ❤️ for data standardization and processing**