# Production Deployment Guide

## Overview

The GLASS Data Standardizer is production-ready with comprehensive error handling, logging, security, and monitoring capabilities.

## Quick Start

### Docker Deployment (Recommended)
```bash
docker-compose up -d
```

### Manual Deployment
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp config/production.env.example config/production.env
# Edit config/production.env

# 3. Run application
python run_production.py
```

## Configuration

### Environment Variables

Required variables (see `config/production.env.example`):
- `ENVIRONMENT`: production
- `DEBUG`: false
- `LOG_LEVEL`: INFO
- `SECRET_KEY`: (auto-generated)
- `MAX_FILE_SIZE_MB`: 100
- `HOST`: 0.0.0.0
- `PORT`: 8501

### Production Features

- ✅ Comprehensive error handling
- ✅ Production logging with rotation
- ✅ Health monitoring
- ✅ Security validation
- ✅ Performance optimization
- ✅ Flexible AMR data cleaning
- ✅ Edge case handling

## Monitoring

- Health endpoint: `http://localhost:8501/health`
- Logs: `logs/app.log`, `logs/errors.log`, `logs/security.log`
- Metrics: Available via health monitor

## Security

- File upload validation
- Rate limiting
- Input sanitization
- Secure defaults

## Support

For issues, check logs in `logs/` directory and review error IDs in the application.

