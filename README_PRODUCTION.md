# GLASS Data Standardizer v2.0.0 - Production Ready

## 🏥 Overview

The GLASS Data Standardizer is a comprehensive data processing and standardization platform designed for healthcare and laboratory data management. It provides intelligent data cleaning, mapping, validation, and analysis capabilities with a focus on antimicrobial resistance (AMR) data processing.

## ✨ Key Features

### 🔄 Core Data Processing
- **Single File Processing**: Upload and standardize individual data files
- **Multiple File Merging**: Intelligently merge multiple files with automatic column mapping
- **Smart Column Mapping**: AI-powered column matching with AST-specific patterns
- **Data Validation**: Comprehensive validation with quality scoring
- **Export Options**: Multiple export formats (Excel, CSV, JSON, XML)

### 🧬 AMR Analytics
- **Enhanced AMR Analysis**: Advanced antimicrobial resistance analysis with CLSI compliance
- **Statistical Rigor**: Confidence intervals, sample size validation, and power analysis
- **Interactive Visualizations**: Professional charts and antibiograms
- **Scientific Reporting**: Comprehensive methodology and results documentation
- **Data Type Detection**: Automatic detection of interpreted vs. breakpoint data

### 🚀 Performance & Production Features
- **Optimized Performance**: Caching, early termination, and efficient algorithms
- **Production Logging**: Structured JSON logging with rotation
- **Health Monitoring**: Real-time system resource monitoring
- **Security**: Input validation, rate limiting, and CSRF protection
- **Docker Support**: Containerized deployment with Docker Compose

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd data-standardizer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the application**
   ```bash
   python run.py
   ```

5. **Access the application**
   - Open your browser to `http://localhost:8501`

## 🐳 Docker Deployment

### Development
```bash
docker-compose up -d
```

### Production
```bash
# Set environment variables
export ENVIRONMENT=production
export SECRET_KEY=your-secure-secret-key

# Deploy
docker-compose -f docker-compose.yml up -d
```

## 📊 Usage Guide

### Single File Workflow
1. **Upload Data**: Select your data file (CSV/Excel)
2. **Map Columns**: Configure column mappings (optional)
3. **Transform Data**: Clean and standardize data values
4. **Validate & Export**: Verify quality and download results

### Multiple File Workflow
1. **Upload Files**: Select multiple files to merge
2. **Merge Data**: Combine files with intelligent mapping
3. **Transform Data**: Clean and standardize merged data
4. **Validate & Export**: Verify quality and download results

### AMR Analytics Workflow
1. **Upload AMR Data**: Upload antimicrobial susceptibility data
2. **Run Analysis**: Generate resistance analysis and visualizations
3. **Review Results**: Interactive dashboards and statistical reports
4. **Export Results**: Download charts, data, and scientific reports

## 🔧 Configuration

### Environment Variables
```bash
# Application Settings
ENVIRONMENT=production
SECRET_KEY=your-secure-secret-key
HOST=0.0.0.0
PORT=8501

# Logging
LOG_LEVEL=INFO
LOG_FILE_APP=logs/app.log
LOG_FILE_ERROR=logs/error.log

# Security
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW_HOURS=1
```

### Application Settings
Access the settings panel in the sidebar to configure:
- File size limits
- Data optimization options
- UI themes
- Performance settings

## 📁 Project Structure

```
data-standardizer/
├── app.py                          # Main application
├── run.py                          # Development launcher
├── run_production.py               # Production launcher
├── requirements.txt                # Dependencies
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Docker Compose setup
├── config/                         # Configuration files
│   ├── production.py              # Production config
│   └── production.env             # Environment variables
├── utils/                          # Core modules
│   ├── file_handler.py            # File upload/processing
│   ├── file_merger.py             # Multi-file merging
│   ├── column_mapper.py           # Column mapping
│   ├── transformer.py             # Data transformation
│   ├── validator.py               # Data validation
│   ├── amr_analytics.py           # AMR analysis engine
│   ├── amr_interface.py           # AMR UI components
│   ├── enhanced_amr_analytics.py  # Enhanced AMR analysis
│   ├── enhanced_amr_interface.py  # Enhanced AMR UI
│   ├── ast_detector.py            # AST data type detection
│   ├── cache_manager.py           # Caching system
│   ├── user_feedback.py           # User feedback system
│   ├── app_settings.py            # Application settings
│   ├── security.py                # Security features
│   ├── health_monitor.py          # Health monitoring
│   └── production_logger.py       # Production logging
├── scripts/                        # Deployment scripts
│   ├── deploy.sh                  # Linux deployment
│   └── deploy.bat                 # Windows deployment
├── data/                          # Sample data directory
└── logs/                          # Log files
```

## 🔒 Security Features

- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: Request rate limiting and IP blocking
- **File Security**: Malicious content scanning
- **CSRF Protection**: Cross-site request forgery protection
- **Security Headers**: HTTP security headers
- **Environment Isolation**: Secure environment variable handling

## 📈 Performance Optimizations

- **Intelligent Caching**: Similarity calculations and column mappings
- **Early Termination**: High-confidence match detection
- **Batch Processing**: Efficient data type handling
- **Memory Management**: Optimized DataFrame operations
- **Progress Indicators**: Real-time operation feedback

## 🧪 Testing

### Manual Testing
1. Upload sample data files
2. Test all workflow types
3. Verify export functionality
4. Check error handling

### Performance Testing
- Test with large files (10,000+ rows)
- Verify memory usage
- Check response times

## 🚀 Deployment

### Production Checklist
- [ ] Set secure SECRET_KEY
- [ ] Configure environment variables
- [ ] Set up logging directories
- [ ] Configure reverse proxy (optional)
- [ ] Set up SSL certificates (optional)
- [ ] Configure backup strategy
- [ ] Set up monitoring

### Health Monitoring
- CPU and memory usage tracking
- Application metrics monitoring
- Error rate monitoring
- Performance metrics

## 📝 Logging

### Log Files
- `logs/app.log`: Application events
- `logs/error.log`: Error messages
- `logs/security.log`: Security events

### Log Rotation
- Automatic log rotation at 10MB
- 5 backup files retained
- JSON structured logging

## 🆘 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Kill existing processes
   taskkill /F /IM python.exe  # Windows
   pkill -f python            # Linux/Mac
   ```

2. **Memory issues**
   - Clear application cache
   - Reduce file size limits
   - Increase system memory

3. **Import errors**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

### Support
- Check logs in `logs/` directory
- Review error messages in application
- Verify environment configuration

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the troubleshooting guide

---

**GLASS Data Standardizer v2.0.0** - Production Ready Data Processing Platform
