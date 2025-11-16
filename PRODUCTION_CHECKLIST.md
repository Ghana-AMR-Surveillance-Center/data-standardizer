# ✅ Production Deployment Checklist

## Pre-Deployment

### Environment Configuration
- [ ] Set `ENVIRONMENT=production`
- [ ] Generate and set strong `SECRET_KEY` (32+ characters)
- [ ] Configure `HOST` and `PORT`
- [ ] Set `DEBUG=false`
- [ ] Set `LOG_LEVEL=INFO` (or WARNING for less verbose)
- [ ] Configure `MAX_FILE_SIZE_MB` appropriately
- [ ] Set `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW`

### Security
- [ ] Review and update `SECRET_KEY`
- [ ] Enable HTTPS (via reverse proxy)
- [ ] Configure firewall rules
- [ ] Review file upload restrictions
- [ ] Configure CORS if needed
- [ ] Set up rate limiting
- [ ] Review input validation rules

### Infrastructure
- [ ] Ensure sufficient disk space (logs, data)
- [ ] Configure log rotation
- [ ] Set up backup procedures
- [ ] Configure monitoring tools
- [ ] Plan for scaling if needed
- [ ] Set up health check endpoints

### Dependencies
- [ ] Install all dependencies: `pip install -r requirements.txt`
- [ ] Verify Python version (3.8+)
- [ ] Test all imports work correctly
- [ ] Check for security vulnerabilities: `pip audit`

## Deployment

### Option 1: Direct Python
- [ ] Run `python run_production.py`
- [ ] Verify application starts
- [ ] Check logs for errors
- [ ] Test health endpoint

### Option 2: Docker
- [ ] Build image: `docker build -t glass-standardizer:latest .`
- [ ] Run container: `docker-compose up -d`
- [ ] Verify container is running
- [ ] Check health: `docker-compose ps`
- [ ] View logs: `docker-compose logs -f`

### Option 3: Systemd Service
- [ ] Create service file
- [ ] Enable service: `sudo systemctl enable glass-standardizer`
- [ ] Start service: `sudo systemctl start glass-standardizer`
- [ ] Check status: `sudo systemctl status glass-standardizer`

## Post-Deployment

### Verification
- [ ] Application accessible at configured URL
- [ ] Health monitoring page works
- [ ] File upload works
- [ ] All workflows functional
- [ ] Error handling works correctly
- [ ] Logs are being written

### Monitoring
- [ ] Set up log monitoring
- [ ] Configure alerts for errors
- [ ] Monitor system resources
- [ ] Track request rates
- [ ] Monitor error rates

### Maintenance
- [ ] Schedule log cleanup
- [ ] Plan dependency updates
- [ ] Schedule security reviews
- [ ] Plan capacity reviews

## Troubleshooting

### Common Issues
1. **Port already in use**: Change PORT environment variable
2. **Permission errors**: Check file permissions for logs/data directories
3. **Import errors**: Verify all dependencies installed
4. **Memory issues**: Reduce MEMORY_LIMIT_MB or increase system memory
5. **Log errors**: Check logs directory permissions

### Support
- Check logs in `logs/` directory
- Review health monitor output
- Check system resources
- Review recent changes
- Contact support with error IDs

