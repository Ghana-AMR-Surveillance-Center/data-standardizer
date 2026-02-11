"""
Production configuration for GLASS Data Standardizer
"""

import os
import secrets
from typing import Dict, Any
from pathlib import Path


class ProductionConfig:
    """Production configuration management"""
    
    def __init__(self):
        """Initialize production configuration with defaults and environment overrides"""
        # Application metadata
        self.version = os.getenv('APP_VERSION', '2.0.0')
        self.environment = os.getenv('ENVIRONMENT', 'production')
        
        # Server configuration
        self.host = os.getenv('HOST', '0.0.0.0')
        self.port = int(os.getenv('PORT', '8501'))
        
        # Security configuration
        self.secret_key = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
        
        # File upload configuration
        max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB', '100'))
        self.max_file_size = max_file_size_mb * 1024 * 1024  # Convert to bytes
        
        # Logging configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'logs/app.log')
        self.log_max_size = int(os.getenv('LOG_MAX_SIZE_MB', '10')) * 1024 * 1024  # 10MB default
        self.log_backup_count = int(os.getenv('LOG_BACKUP_COUNT', '5'))
        
        # Debug mode
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        # Data processing configuration
        self.chunk_size = int(os.getenv('CHUNK_SIZE', '10000'))
        self.max_memory_usage_mb = int(os.getenv('MAX_MEMORY_USAGE_MB', '500'))
        
        # Ensure logs directory exists
        Path('logs').mkdir(exist_ok=True)
    
    def validate_config(self) -> bool:
        """
        Validate production configuration
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        try:
            # Check required directories
            required_dirs = ['logs']
            for dir_path in required_dirs:
                Path(dir_path).mkdir(exist_ok=True)
            
            # Validate port range
            if not (1 <= self.port <= 65535):
                return False
            
            # Validate log level
            valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if self.log_level.upper() not in valid_log_levels:
                return False
            
            # Validate file size (must be positive)
            if self.max_file_size <= 0:
                return False
            
            # Validate secret key exists
            if not self.secret_key or len(self.secret_key) < 16:
                return False
            
            return True
        except Exception:
            return False
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get logging configuration dictionary
        
        Returns:
            Dict[str, Any]: Logging configuration
        """
        return {
            'log_level': self.log_level,
            'log_file': self.log_file,
            'log_max_size': self.log_max_size,
            'log_backup_count': self.log_backup_count,
            'environment': self.environment,
            'debug': self.debug
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """
        Get security configuration dictionary
        
        Returns:
            Dict[str, Any]: Security configuration
        """
        return {
            'secret_key': self.secret_key,
            'max_file_size': self.max_file_size,
            'max_file_size_mb': self.max_file_size / (1024 * 1024)
        }
    
    def get_server_config(self) -> Dict[str, Any]:
        """
        Get server configuration dictionary
        
        Returns:
            Dict[str, Any]: Server configuration
        """
        return {
            'host': self.host,
            'port': self.port,
            'debug': self.debug
        }


# Global production config instance
production_config = ProductionConfig()

