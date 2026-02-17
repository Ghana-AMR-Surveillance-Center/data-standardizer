# 🏥 AMR Data Harmonizer

**Advanced Data Processing & Standardization Platform for AMR Surveillance**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)](https://streamlit.io)
[![CI/CD Pipeline](https://github.com/Ghana-AMR-Surveillance-Center/data-standardizer/actions/workflows/ci.yml/badge.svg)](https://github.com/Ghana-AMR-Surveillance-Center/data-standardizer/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A comprehensive platform designed to address critical data cleaning challenges in **Antimicrobial Resistance (AMR) surveillance** across African laboratories. This tool helps laboratories prepare their data for submission to global surveillance systems like GLASS and WHONET.

## 🚀 Quick Start

### Option 1: Streamlit Cloud Deployment (Recommended for Sharing)
[![Deploy to Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

1. Push your code to GitHub (this repository)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository: `drmichaeladu/data-standardizer`
4. Set main file path: `app.py`
5. Click "Deploy" and wait for deployment to complete
6. Your app will be live at `https://your-app-name.streamlit.app`

**Note**: For Streamlit Cloud, ensure your `requirements.txt` includes all dependencies.

### Option 2: Local Development Setup

#### Windows (Easy Launch)
```bash
# Double-click or run (starts in detached mode - works in all terminals):
launch.bat

# For interactive logs in CMD, use:
launch.bat -f
```

#### Linux/macOS
```bash
# Make scripts executable
chmod +x deploy_production.sh scripts/deploy.sh

# Run deployment script
./deploy_production.sh
```

### Option 3: Manual Setup (Local)

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
# OR for production mode:
python run_production.py
```

### Option 4: Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access at http://localhost:8501
```

## 📋 System Requirements

- **Python**: 3.8 or higher (3.10+ recommended)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 1GB free space
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)

## ✨ Features

### Core Functionality
- **📁 Single File Processing**: Upload, analyze, transform, and export individual files
  - Column mapping & renaming
  - Data transformation and cleaning
  - Quality validation
  - Multi-format export (CSV, Excel, JSON, XML)

- **📊 Multiple File Merging**: Intelligent merging of multiple Excel/CSV files
  - **🆕 Excel Sheet Selection**: Choose specific sheets from Excel files before merging
  - Smart column matching with fuzzy logic
  - Automatic data harmonization
  - Duplicate detection and audit
  - Shared column mapping across files
  - One-file-at-a-time processing workflow

- **🧬 AMR Analytics**: Professional antimicrobial resistance analysis with CLSI compliance
  - CLSI-compliant analysis (M100-S33, M02-A13)
  - Resistance rate calculations with confidence intervals
  - MDR/XDR/PDR classification
  - Professional visualizations and heatmaps
  - Statistical validation

- **🎯 Data Preparation Wizards**:
  - **GLASS Preparation Wizard**: Step-by-step guided process for GLASS submission
  - **WHONET Preparation Wizard**: Step-by-step guided process for WHONET import
  - Automatic data cleaning and standardization
  - Built-in format validation
  - Comprehensive quality reports

### Advanced Features
- **🔗 Smart Column Mapping**: AI-powered column matching with fuzzy matching and AST-specific patterns
- **🔄 Data Transformation**: Comprehensive data cleaning and standardization
- **📈 Quality Assessment**: Advanced data quality metrics and validation
- **📤 Multi-format Export**: Export to CSV, Excel, JSON, XML formats
- **🛡️ Production Ready**: Error handling, logging, monitoring, and security

### Production Features
- **🛡️ Error Handling**: Comprehensive error logging and recovery
- **📊 Performance Monitoring**: Real-time performance metrics and optimization
- **✅ Data Validation**: Multi-level data validation and quality checks
- **💾 Memory Optimization**: Automatic DataFrame optimization
- **⚙️ Configuration Management**: Centralized settings and customization
- **🔒 Security**: File upload validation, rate limiting, input sanitization

## 🏗️ Architecture

```
data-standardizer/
├── app.py                      # Main Streamlit application
├── run.py                      # Development launcher
├── run_production.py           # Production launcher
├── launch.bat                  # Windows quick launcher
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
├── docker-compose.yml          # Docker deployment config
├── deploy_production.sh        # Production deployment script
│
├── config/                     # Configuration modules
│   ├── __init__.py
│   └── production.py          # Production configuration
│
├── utils/                      # Core utility modules
│   ├── amr_analytics.py       # AMR analysis engine (CLSI compliant)
│   ├── amr_data_quality.py    # AMR-specific quality assessment
│   ├── amr_interface.py       # AMR analytics interface
│   ├── enhanced_amr_interface.py  # Enhanced AMR interface
│   ├── app_config.py          # Configuration management
│   ├── app_settings.py        # Enhanced settings management
│   ├── ast_detector.py        # AST data type detection
│   ├── cache_manager.py       # Advanced caching system
│   ├── column_mapper.py       # Intelligent column mapping
│   ├── column_utils.py        # Column utilities
│   ├── data_profiler.py       # Data profiling and analysis
│   ├── data_quality.py        # Data quality assessment
│   ├── error_handler.py       # Error handling system
│   ├── excel_exporter.py      # Multi-format export
│   ├── file_handler.py        # File processing
│   ├── file_merger.py         # File merging logic (with sheet selection)
│   ├── glass_standardizer.py  # GLASS format standardization
│   ├── glass_wizard.py        # GLASS preparation wizard
│   ├── whonet_standardizer.py # WHONET format standardization
│   ├── whonet_wizard.py       # WHONET preparation wizard
│   ├── helpers.py             # Helper functions
│   ├── logger.py              # Logging system
│   ├── performance_monitor.py # Performance monitoring
│   ├── production_error_handler.py  # Production error handling
│   ├── production_logger.py   # Production logging
│   ├── schema_analyzer.py     # Schema analysis
│   ├── security.py            # Security validation
│   ├── session_manager.py     # Session state management
│   ├── transformer.py         # Data transformation
│   ├── ui_components.py       # UI components
│   ├── ui_validator.py        # UI validation
│   ├── user_feedback.py       # Enhanced user feedback system
│   └── validator.py           # Validation logic
│
├── scripts/                    # Deployment scripts
│   ├── deploy.bat             # Windows deployment script
│   └── deploy.sh              # Linux/macOS deployment script
│
├── docs/                       # Documentation
│   └── PRODUCTION_GUIDE.md    # Production deployment guide
│
└── deployment/                 # Deployment documentation
    └── README.md              # Deployment guide
```

## 🔧 Usage

### Single File Workflow
1. **Upload**: Select and upload your data file (CSV, Excel)
2. **Analyze**: Review data structure and quality metrics
3. **Map**: Configure column mappings to target schema (optional)
4. **Transform**: Apply data cleaning and standardization
5. **Validate**: Verify data quality and completeness
6. **Export**: Download processed data in your preferred format

### Multiple File Workflow (with Excel Sheet Selection)
1. **Upload**: Select multiple files for merging
2. **Select Sheets**: For Excel files, choose which sheet to merge from each file
3. **Validate**: Review file structures and compatibility
4. **Map**: Configure column mappings between files (shared mapping across files)
5. **Merge**: Combine files one at a time with intelligent data handling
6. **Audit Duplicates**: Review and decide on duplicate row handling
7. **Review**: Analyze merge statistics and data quality
8. **Export**: Download merged dataset

### GLASS/WHONET Preparation Wizards
1. **Choose Wizard**: Select GLASS or WHONET preparation wizard
2. **Upload Data**: Upload your AMR data file
3. **Follow Steps**: Complete the guided step-by-step process
4. **Review Quality**: Check comprehensive data quality assessment
5. **Apply Fixes**: Use auto-fix options if needed
6. **Export**: Download your standardized, submission-ready data

## 🛠️ Configuration

The application uses a centralized configuration system:

- **App Settings**: File size limits, memory usage, processing options
- **UI Settings**: Theme, layout, display preferences
- **Data Processing**: Chunk sizes, optimization settings
- **Merging**: Similarity thresholds, mapping preferences, sheet selection
- **Export**: Default formats, compression options

### Environment Variables

For production deployment, set these environment variables:

```bash
ENVIRONMENT=production
SECRET_KEY=your-secret-key-here
HOST=0.0.0.0
PORT=8501
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=100
```

## 📊 Data Quality Metrics

- **Completeness**: Percentage of non-null values
- **Consistency**: Data format and value consistency
- **Accuracy**: Data accuracy validation
- **Validity**: Data validity checks
- **Uniqueness**: Duplicate detection and analysis
- **AMR-Specific**: Organism name standardization, antimicrobial result validation, GLASS/WHONET compliance

## 🚀 Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository: `drmichaeladu/data-standardizer`
4. Set main file: `app.py`
5. Deploy!

### Docker

```bash
docker-compose up -d
```

### Production Server

```bash
# Linux/macOS
./deploy_production.sh

# Windows
scripts\deploy.bat
```

## 🧪 Testing

Run the unit test suite:

```bash
pip install -r requirements.txt  # includes pytest
python -m pytest tests/ -v
```

Tests cover file handling, validation, column utilities, and CSV/Excel formula injection protection.

## 🔍 Troubleshooting

### Common Issues

1. **Python Not Found**
   - Install Python 3.8+ from https://python.org
   - Ensure Python is in PATH

2. **Dependencies Not Installing**
   - Check internet connection
   - Try: `pip install --upgrade pip`
   - Run: `pip install -r requirements.txt`

3. **Port Already in Use**
   - Windows: `taskkill /f /im python.exe`
   - Linux/macOS: `pkill -f streamlit`
   - Or use different port: `streamlit run app.py --server.port 8502`

4. **Virtual Environment Issues**
   - Delete `.venv` folder and recreate
   - Ensure you have write permissions

5. **Excel File Issues**
   - Ensure `openpyxl` and `xlrd` are installed
   - Check file is not corrupted
   - Try opening file in Excel first

### Getting Help

- Check the error messages in the terminal
- Review the application logs in `logs/` directory
- Ensure all system requirements are met
- Try running as administrator if on Windows
- Check the [Production Guide](docs/PRODUCTION_GUIDE.md) for deployment issues

## 📈 Performance

- **Memory Optimization**: Automatic DataFrame optimization
- **Chunked Processing**: Large file handling
- **Caching**: Intelligent data caching
- **Monitoring**: Real-time performance metrics
- **Sheet Selection**: Efficient Excel file processing

## 🔒 Security

- **Input Validation**: All inputs are validated
- **File Upload Limits**: Configurable file size restrictions
- **CSV/Excel Formula Injection Protection**: Cells starting with `=`, `+`, `-`, `@` are sanitized to prevent execution when files are opened in Excel
- **Error Information**: Controlled error disclosure
- **Memory Management**: Automatic cleanup
- **Security Validation**: File type and content validation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📞 Support

For technical support or issues:
- **Email**: drmichaeladu@gmail.com
- **Repository**: [drmichaeladu/data-standardizer](https://github.com/drmichaeladu/data-standardizer)
- Check the troubleshooting section above
- Review the application logs
- Check the [Production Guide](docs/PRODUCTION_GUIDE.md)

## 🎯 Recent Updates

### Version 2.0.0 (Latest)
- ✅ **Excel Sheet Selection**: Choose specific sheets from Excel files during merging
- ✅ **Shared Column Mapping**: Column mappings are saved and reused across files
- ✅ **GLASS Preparation Wizard**: Step-by-step guided process for GLASS submission
- ✅ **WHONET Preparation Wizard**: Step-by-step guided process for WHONET import
- ✅ **Enhanced AMR Analytics**: CLSI-compliant analysis with statistical validation
- ✅ **Production Ready**: Comprehensive error handling, logging, and monitoring
- ✅ **Performance Optimizations**: Memory management and caching improvements

---

**Version**: 2.0.0  
**Last Updated**: February 2025  
**Compatibility**: Python 3.8+, Windows 10+, macOS 10.14+, Linux Ubuntu 18.04+  
**Repository**: [drmichaeladu/data-standardizer](https://github.com/drmichaeladu/data-standardizer)

**Made with ❤️ for AMR surveillance data standardization and processing**


---

## 👥 Contributing

We welcome contributions from the community! This project is maintained by the Ghana AMR Surveillance Center team and aims to improve antimicrobial resistance data standardization across Africa.

### How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.

### Continuous Integration

This project uses GitHub Actions for automated testing. The CI/CD pipeline:

- **Runs automatically** on every push and pull request to any branch
- **Tests multiple Python versions**: 3.8, 3.9, 3.10, and 3.11
- **Executes integration tests**: Validates that all modules can be imported and work together
- **Verifies production readiness**: Checks dependencies, file structure, and configurations

The workflow file is located at `.github/workflows/ci.yml`. All tests must pass before merging pull requests.

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Ghana Health Service for supporting AMR surveillance initiatives
- The Aurum Institute for technical guidance
- All contributors who have helped improve this platform
