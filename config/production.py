"""
Production configuration for GLASS Data Standardizer
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path

class ProductionConfig:
    """Production configuration management"""
    
    def __init__(self):
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Application settings
        self.app_name = "GLASS Data Standardizer"
        self.version = "2.0.0"
        self.host = os.getenv('HOST', '0.0.0.0')
        self.port = int(os.getenv('PORT', '8501'))
        
        # Security settings
        self.secret_key = os.getenv('SECRET_KEY', self._generate_secret_key())
        self.max_file_size = int(os.getenv('MAX_FILE_SIZE_MB', '100')) * 1024 * 1024
        self.allowed_extensions = ['.csv', '.xlsx', '.xls']
        self.rate_limit_requests = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
        self.rate_limit_window = int(os.getenv('RATE_LIMIT_WINDOW', '3600'))
        
        # Database settings (if needed)
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///app.db')
        
        # Cache settings
        self.cache_type = os.getenv('CACHE_TYPE', 'memory')
        self.cache_ttl = int(os.getenv('CACHE_TTL', '3600'))
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        
        # Monitoring settings
        self.enable_monitoring = os.getenv('ENABLE_MONITORING', 'true').lower() == 'true'
        self.metrics_port = int(os.getenv('METRICS_PORT', '9090'))
        self.health_check_interval = int(os.getenv('HEALTH_CHECK_INTERVAL', '30'))
        
        # Logging settings
        self.log_file = os.getenv('LOG_FILE', 'logs/app.log')
        self.log_max_size = int(os.getenv('LOG_MAX_SIZE', '10485760'))  # 10MB
        self.log_backup_count = int(os.getenv('LOG_BACKUP_COUNT', '5'))
        
        # Performance settings
        self.max_workers = int(os.getenv('MAX_WORKERS', '4'))
        self.memory_limit = int(os.getenv('MEMORY_LIMIT_MB', '2048'))
        self.chunk_size = int(os.getenv('CHUNK_SIZE', '1000'))
        
        # Feature flags
        self.enable_amr_analytics = os.getenv('ENABLE_AMR_ANALYTICS', 'true').lower() == 'true'
        self.enable_file_merging = os.getenv('ENABLE_FILE_MERGING', 'true').lower() == 'true'
        self.enable_data_quality = os.getenv('ENABLE_DATA_QUALITY', 'true').lower() == 'true'
        
        # External services
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.admin_email = os.getenv('ADMIN_EMAIL')
        
    def _generate_secret_key(self) -> str:
        """Generate a secret key for production"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            'url': self.database_url,
            'pool_size': 10,
            'max_overflow': 20,
            'pool_timeout': 30,
            'pool_recycle': 3600
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration"""
        return {
            'url': self.redis_url,
            'decode_responses': True,
            'socket_timeout': 5,
            'socket_connect_timeout': 5,
            'retry_on_timeout': True
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                },
                'detailed': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': self.log_level,
                    'formatter': 'standard',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': self.log_level,
                    'formatter': 'detailed',
                    'filename': self.log_file,
                    'maxBytes': self.log_max_size,
                    'backupCount': self.log_backup_count
                }
            },
            'loggers': {
                '': {
                    'handlers': ['console', 'file'],
                    'level': self.log_level,
                    'propagate': False
                }
            }
        }
    
    def validate_config(self) -> bool:
        """Validate production configuration"""
        # For development, we'll use defaults if environment variables are missing
        if self.environment == 'development':
            return True
        
        required_vars = [
            'SECRET_KEY',
            'HOST',
            'PORT'
        ]
        
        missing_vars = []
        warnings = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        # Validate SECRET_KEY strength if provided
        if os.getenv('SECRET_KEY'):
            secret_key = os.getenv('SECRET_KEY')
            if len(secret_key) < 32:
                warnings.append("SECRET_KEY should be at least 32 characters long for production")
        
        # Validate PORT is a valid number
        if os.getenv('PORT'):
            try:
                port = int(os.getenv('PORT'))
                if port < 1 or port > 65535:
                    warnings.append(f"PORT {port} is outside valid range (1-65535)")
            except ValueError:
                missing_vars.append('PORT')  # Invalid port is treated as missing
        
        # Log warnings if any
        if warnings:
            import logging
            logger = logging.getLogger(__name__)
            for warning in warnings:
                logger.warning(f"Configuration warning: {warning}")
        
        if missing_vars:
            # Missing required environment variables - will be logged
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        return True
    
    def get_streamlit_config(self) -> Dict[str, Any]:
        """Get Streamlit configuration for production"""
        return {
            'server': {
                'port': self.port,
                'address': self.host,
                'headless': True,
                'enableCORS': False,
                'enableXsrfProtection': True,
                'maxUploadSize': self.max_file_size,
                'maxMessageSize': self.max_file_size
            },
            'browser': {
                'gatherUsageStats': False
            },
            'theme': {
                'primaryColor': '#1f77b4',
                'backgroundColor': '#ffffff',
                'secondaryBackgroundColor': '#f0f2f6',
                'textColor': '#262730'
            },
            'logger': {
                'level': self.log_level
            }
        }

# Global production config instance
production_config = ProductionConfig()
