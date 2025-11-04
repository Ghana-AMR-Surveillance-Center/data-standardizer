# 🚀 GLASS Data Standardizer - Production Deployment Guide

## **📋 Overview**

This guide provides comprehensive instructions for deploying the GLASS Data Standardizer in a production environment with enterprise-grade features including security, monitoring, logging, and scalability.

## **🏗️ Production Architecture**

### **Core Components:**
- **Application**: Streamlit-based web application
- **Security**: Input validation, rate limiting, CSRF protection
- **Monitoring**: Health checks, performance metrics, alerting
- **Logging**: Structured logging with rotation and analysis
- **Caching**: Redis-based caching for performance
- **Deployment**: Docker containerization with orchestration

### **Production Features:**
- ✅ **Security**: Comprehensive input validation and protection
- ✅ **Monitoring**: Real-time health checks and performance metrics
- ✅ **Logging**: Structured logging with rotation and analysis
- ✅ **Caching**: Intelligent caching for improved performance
- ✅ **Scalability**: Docker-based deployment with load balancing
- ✅ **Reliability**: Health checks, auto-restart, and error recovery

## **🔧 Prerequisites**

### **System Requirements:**
- **OS**: Linux (Ubuntu 20.04+), Windows Server 2019+, or macOS 10.15+
- **CPU**: 2+ cores (4+ recommended)
- **RAM**: 4GB minimum (8GB+ recommended)
- **Storage**: 20GB+ available space
- **Network**: Port 8501 accessible

### **Software Requirements:**
- **Python**: 3.8+ (3.11+ recommended)
- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 2.0+ (for orchestration)
- **Git**: 2.0+ (for version control)

## **📦 Installation Methods**

### **Method 1: Docker Deployment (Recommended)**

#### **1. Clone Repository**
```bash
git clone <repository-url>
cd data-standardizer
```

#### **2. Configure Environment**
```bash
# Copy production environment template
cp config/production.env .env

# Edit environment variables
nano .env
```

#### **3. Deploy with Docker Compose**
```bash
# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### **4. Access Application**
- **URL**: http://localhost:8501
- **Health Check**: http://localhost:8501/_stcore/health

### **Method 2: Direct Python Deployment**

#### **1. Setup Environment**
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### **2. Configure Production Settings**
```bash
# Set environment variables
export ENVIRONMENT=production
export DEBUG=false
export LOG_LEVEL=INFO
export SECRET_KEY=your-secret-key-here
```

#### **3. Launch Application**
```bash
# Using production launcher
python run_production.py

# Or using standard launcher
python run.py
```

## **⚙️ Configuration**

### **Environment Variables**

#### **Core Settings:**
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8501
```

#### **Security Settings:**
```bash
SECRET_KEY=your-secret-key-here-change-in-production
MAX_FILE_SIZE_MB=100
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

#### **Performance Settings:**
```bash
MAX_WORKERS=4
MEMORY_LIMIT_MB=2048
CHUNK_SIZE=1000
CACHE_TTL=3600
```

#### **Monitoring Settings:**
```bash
ENABLE_MONITORING=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30
```

### **Configuration Files**

#### **Production Config** (`config/production.py`)
- Centralized configuration management
- Environment-specific settings
- Validation and defaults

#### **Environment File** (`config/production.env`)
- Environment variables template
- Security settings
- Feature flags

## **🔒 Security Configuration**

### **Input Validation**
- File upload validation
- SQL injection prevention
- XSS protection
- Path traversal prevention

### **Rate Limiting**
- Request rate limiting
- File upload limits
- IP-based blocking

### **Security Headers**
- Content Security Policy
- X-Frame-Options
- X-Content-Type-Options
- Strict-Transport-Security

### **File Security**
- File type validation
- Malicious content detection
- Size limits
- Signature verification

## **📊 Monitoring and Logging**

### **Health Monitoring**
- System resource monitoring
- Application health checks
- Performance metrics
- Alert thresholds

### **Logging System**
- Structured JSON logging
- Log rotation and retention
- Security event logging
- Performance metrics logging

### **Metrics Collection**
- Request/response metrics
- File processing metrics
- Error rates and types
- System resource usage

## **🚀 Deployment Scripts**

### **Windows Deployment**
```cmd
# Run deployment script
scripts\deploy.bat

# Available commands:
scripts\deploy.bat deploy    # Deploy application
scripts\deploy.bat status    # Check status
scripts\deploy.bat logs      # View logs
scripts\deploy.bat stop      # Stop application
```

### **Linux/macOS Deployment**
```bash
# Make script executable
chmod +x scripts/deploy.sh

# Run deployment script
./scripts/deploy.sh

# Available commands:
./scripts/deploy.sh deploy    # Deploy application
./scripts/deploy.sh rollback  # Rollback to previous version
./scripts/deploy.sh status    # Check status
./scripts/deploy.sh logs      # View logs
./scripts/deploy.sh stop      # Stop application
```

## **🔍 Health Checks**

### **Application Health**
- **Endpoint**: `/_stcore/health`
- **Response**: JSON with status information
- **Checks**: Database, memory, disk, CPU

### **Monitoring Endpoints**
- **Health**: `/health` - Overall application health
- **Metrics**: `/metrics` - Performance metrics
- **Logs**: `/logs` - Recent log entries

### **Health Check Script**
```bash
# Check application health
curl -f http://localhost:8501/_stcore/health

# Check detailed health
curl http://localhost:8501/health
```

## **📈 Performance Optimization**

### **Caching Strategy**
- Redis-based caching
- File processing cache
- Analysis result cache
- Configurable TTL

### **Memory Management**
- Automatic DataFrame optimization
- Memory usage monitoring
- Garbage collection tuning
- Memory leak detection

### **Processing Optimization**
- Chunked file processing
- Parallel processing
- Background task processing
- Resource usage limits

## **🛠️ Maintenance**

### **Log Management**
```bash
# View application logs
docker-compose logs -f glass-data-standardizer

# View specific log files
tail -f logs/app.log
tail -f logs/errors.log
tail -f logs/security.log
```

### **Backup and Recovery**
```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Backup configuration
cp -r config/ backup-config-$(date +%Y%m%d)/
```

### **Updates and Upgrades**
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## **🔧 Troubleshooting**

### **Common Issues**

#### **Application Won't Start**
```bash
# Check logs
docker-compose logs glass-data-standardizer

# Check configuration
python -c "from config.production import production_config; print(production_config.validate_config())"

# Check dependencies
pip list | grep streamlit
```

#### **Performance Issues**
```bash
# Check resource usage
docker stats

# Check health metrics
curl http://localhost:8501/health

# Check logs for errors
grep ERROR logs/app.log
```

#### **Security Issues**
```bash
# Check security logs
tail -f logs/security.log

# Check rate limiting
grep "rate limit" logs/app.log

# Check blocked IPs
grep "blocked" logs/security.log
```

### **Debug Mode**
```bash
# Enable debug mode
export DEBUG=true
export LOG_LEVEL=DEBUG

# Restart application
docker-compose restart glass-data-standardizer
```

## **📋 Production Checklist**

### **Pre-Deployment**
- [ ] Environment variables configured
- [ ] Security settings reviewed
- [ ] Monitoring enabled
- [ ] Logging configured
- [ ] Backup strategy in place

### **Post-Deployment**
- [ ] Health checks passing
- [ ] Monitoring alerts configured
- [ ] Log rotation working
- [ ] Performance metrics normal
- [ ] Security logs clean

### **Ongoing Maintenance**
- [ ] Regular log review
- [ ] Performance monitoring
- [ ] Security updates
- [ ] Backup verification
- [ ] Capacity planning

## **📞 Support and Monitoring**

### **Monitoring Dashboard**
- **Application**: http://localhost:8501
- **Health**: http://localhost:8501/health
- **Metrics**: http://localhost:8501/metrics

### **Log Locations**
- **Application**: `logs/app.log`
- **Errors**: `logs/errors.log`
- **Security**: `logs/security.log`

### **Alert Thresholds**
- **Memory Usage**: >85%
- **CPU Usage**: >80%
- **Disk Usage**: >90%
- **Error Rate**: >5%
- **Response Time**: >5s

---

**Version**: 2.0.0 Production  
**Last Updated**: 2025  
**Status**: Production Ready ✅
