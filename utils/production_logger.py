"""
Production logging system for GLASS Data Standardizer
"""

import logging
import logging.handlers
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import traceback

class ProductionLogger:
    """Enhanced logging system for production"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('glass_data_standardizer')
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup production logging configuration"""
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set log level
        log_level = getattr(logging, self.config.get('log_level', 'INFO').upper())
        self.logger.setLevel(log_level)
        
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            filename=self.config.get('log_file', 'logs/app.log'),
            maxBytes=self.config.get('log_max_size', 10 * 1024 * 1024),  # 10MB
            backupCount=self.config.get('log_backup_count', 5)
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            filename='logs/errors.log',
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)
        
        # Security log handler
        security_handler = logging.handlers.RotatingFileHandler(
            filename='logs/security.log',
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3
        )
        security_handler.setLevel(logging.WARNING)
        security_formatter = logging.Formatter(
            '%(asctime)s [SECURITY] %(levelname)s: %(message)s'
        )
        security_handler.setFormatter(security_formatter)
        self.logger.addHandler(security_handler)
    
    def log_request(self, method: str, endpoint: str, status_code: int, 
                   processing_time: float, user_ip: str = None, user_agent: str = None):
        """Log HTTP request"""
        log_data = {
            'type': 'request',
            'method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'processing_time': processing_time,
            'user_ip': user_ip,
            'user_agent': user_agent,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Request: {json.dumps(log_data)}")
    
    def log_file_upload(self, filename: str, file_size: int, processing_time: float,
                       success: bool, error_message: str = None):
        """Log file upload"""
        log_data = {
            'type': 'file_upload',
            'filename': filename,
            'file_size': file_size,
            'processing_time': processing_time,
            'success': success,
            'error_message': error_message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if success:
            self.logger.info(f"File upload: {json.dumps(log_data)}")
        else:
            self.logger.error(f"File upload failed: {json.dumps(log_data)}")
    
    def log_data_processing(self, operation: str, records_processed: int,
                           processing_time: float, success: bool, error_message: str = None):
        """Log data processing operation"""
        log_data = {
            'type': 'data_processing',
            'operation': operation,
            'records_processed': records_processed,
            'processing_time': processing_time,
            'success': success,
            'error_message': error_message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if success:
            self.logger.info(f"Data processing: {json.dumps(log_data)}")
        else:
            self.logger.error(f"Data processing failed: {json.dumps(log_data)}")
    
    def log_security_event(self, event_type: str, details: Dict[str, Any],
                          severity: str = 'warning', user_ip: str = None):
        """Log security event"""
        log_data = {
            'type': 'security_event',
            'event_type': event_type,
            'details': details,
            'severity': severity,
            'user_ip': user_ip,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if severity == 'critical':
            self.logger.critical(f"Security event: {json.dumps(log_data)}")
        elif severity == 'error':
            self.logger.error(f"Security event: {json.dumps(log_data)}")
        else:
            self.logger.warning(f"Security event: {json.dumps(log_data)}")
    
    def log_performance_metric(self, metric_name: str, value: float, 
                              unit: str = None, context: Dict[str, Any] = None):
        """Log performance metric"""
        log_data = {
            'type': 'performance_metric',
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Performance metric: {json.dumps(log_data)}")
    
    def log_application_start(self, version: str, environment: str):
        """Log application startup"""
        log_data = {
            'type': 'application_start',
            'version': version,
            'environment': environment,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Application started: {json.dumps(log_data)}")
    
    def log_application_stop(self, reason: str = 'normal'):
        """Log application shutdown"""
        log_data = {
            'type': 'application_stop',
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Application stopped: {json.dumps(log_data)}")
    
    def log_error(self, error: Exception, context: str = None, 
                  user_id: str = None, request_id: str = None):
        """Log error with full context"""
        log_data = {
            'type': 'error',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'user_id': user_id,
            'request_id': request_id,
            'traceback': traceback.format_exc(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.error(f"Error occurred: {json.dumps(log_data)}")
    
    def log_user_action(self, action: str, user_id: str = None, 
                       details: Dict[str, Any] = None):
        """Log user action"""
        log_data = {
            'type': 'user_action',
            'action': action,
            'user_id': user_id,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"User action: {json.dumps(log_data)}")
    
    def log_system_event(self, event: str, details: Dict[str, Any] = None):
        """Log system event"""
        log_data = {
            'type': 'system_event',
            'event': event,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"System event: {json.dumps(log_data)}")
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        log_files = []
        log_dir = Path('logs')
        
        if log_dir.exists():
            for log_file in log_dir.glob('*.log*'):
                stat = log_file.stat()
                log_files.append({
                    'filename': log_file.name,
                    'size_bytes': stat.st_size,
                    'size_mb': stat.st_size / (1024 * 1024),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return {
            'log_files': log_files,
            'total_files': len(log_files),
            'total_size_mb': sum(f['size_mb'] for f in log_files)
        }
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up old log files"""
        log_dir = Path('logs')
        if not log_dir.exists():
            return
        
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
        cleaned_files = []
        
        for log_file in log_dir.glob('*.log*'):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    cleaned_files.append(log_file.name)
                except Exception as e:
                    self.logger.error(f"Failed to delete log file {log_file.name}: {str(e)}")
        
        if cleaned_files:
            self.logger.info(f"Cleaned up {len(cleaned_files)} old log files: {cleaned_files}")

# Global production logger instance
production_logger = None

def initialize_production_logger(config: Dict[str, Any]):
    """Initialize the global production logger"""
    global production_logger
    production_logger = ProductionLogger(config)
    return production_logger

def get_production_logger() -> Optional[ProductionLogger]:
    """Get the global production logger"""
    return production_logger
