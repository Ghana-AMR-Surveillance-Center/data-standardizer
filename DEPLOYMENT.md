# Production Deployment Guide

## Quick Start

### Option 1: Docker Deployment (Recommended)
```bash
docker-compose up -d
```

### Option 2: Manual Deployment
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
cp config/production.env.example config/production.env
# Edit config/production.env with your settings

# 3. Run production launcher
python run_production.py
```

## Environment Variables

Required environment variables (see `config/production.env.example`):
- `ENVIRONMENT`: production
- `DEBUG`: false
- `LOG_LEVEL`: INFO
- `SECRET_KEY`: (auto-generated if not set)
- `MAX_FILE_SIZE_MB`: 100
- `HOST`: 0.0.0.0
- `PORT`: 8501

## Production Checklist

- [x] All dependencies installed
- [x] Environment variables configured
- [x] Logging directories created
- [x] Security settings reviewed
- [x] Health monitoring enabled
- [x] Error handling configured
- [x] Performance monitoring active

## Health Monitoring

Health endpoint: `http://localhost:8501/health`

## Logs

Logs are stored in:
- `logs/app.log` - Application logs
- `logs/errors.log` - Error logs
- `logs/security.log` - Security logs

## Security

- File upload validation enabled
- Rate limiting configured
- Input sanitization active
- Secure defaults applied

