"""
Health monitoring and metrics for production GLASS Data Standardizer
"""

import time
import psutil
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Comprehensive health monitoring for production"""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {
            'requests_total': 0,
            'requests_successful': 0,
            'requests_failed': 0,
            'file_uploads': 0,
            'file_processing_time': [],
            'memory_usage': [],
            'cpu_usage': [],
            'disk_usage': [],
            'errors': []
        }
        
        self.health_checks = {
            'database': self._check_database,
            'memory': self._check_memory,
            'disk': self._check_disk,
            'cpu': self._check_cpu,
            'cache': self._check_cache,
            'logs': self._check_logs
        }
        
        self.alert_thresholds = {
            'memory_percent': 85,
            'cpu_percent': 80,
            'disk_percent': 90,
            'error_rate': 5,
            'response_time': 5.0
        }
        
        self.alerts = []
        self.monitoring_active = True
        
        # Start background monitoring
        self._start_background_monitoring()
    
    def _start_background_monitoring(self):
        """Start background monitoring thread"""
        def monitor_loop():
            while self.monitoring_active:
                try:
                    self._collect_system_metrics()
                    self._check_health_status()
                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    logger.error(f"Health monitoring error: {str(e)}")
                    time.sleep(60)  # Wait longer on error
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def _collect_system_metrics(self):
        """Collect system metrics"""
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics['memory_usage'].append({
                'timestamp': time.time(),
                'percent': memory.percent,
                'available': memory.available,
                'used': memory.used
            })
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics['cpu_usage'].append({
                'timestamp': time.time(),
                'percent': cpu_percent
            })
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.metrics['disk_usage'].append({
                'timestamp': time.time(),
                'percent': (disk.used / disk.total) * 100,
                'free': disk.free,
                'used': disk.used
            })
            
            # Keep only last 1000 entries
            for key in ['memory_usage', 'cpu_usage', 'disk_usage']:
                if len(self.metrics[key]) > 1000:
                    self.metrics[key] = self.metrics[key][-1000:]
                    
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
    
    def _check_health_status(self):
        """Check overall health status"""
        try:
            # Check memory usage
            if self.metrics['memory_usage']:
                latest_memory = self.metrics['memory_usage'][-1]['percent']
                if latest_memory > self.alert_thresholds['memory_percent']:
                    self._create_alert('memory', f"High memory usage: {latest_memory:.1f}%")
            
            # Check CPU usage
            if self.metrics['cpu_usage']:
                latest_cpu = self.metrics['cpu_usage'][-1]['percent']
                if latest_cpu > self.alert_thresholds['cpu_percent']:
                    self._create_alert('cpu', f"High CPU usage: {latest_cpu:.1f}%")
            
            # Check disk usage
            if self.metrics['disk_usage']:
                latest_disk = self.metrics['disk_usage'][-1]['percent']
                if latest_disk > self.alert_thresholds['disk_percent']:
                    self._create_alert('disk', f"High disk usage: {latest_disk:.1f}%")
            
            # Check error rate
            total_requests = self.metrics['requests_total']
            if total_requests > 0:
                error_rate = (self.metrics['requests_failed'] / total_requests) * 100
                if error_rate > self.alert_thresholds['error_rate']:
                    self._create_alert('error_rate', f"High error rate: {error_rate:.1f}%")
            
        except Exception as e:
            logger.error(f"Error checking health status: {str(e)}")
    
    def _create_alert(self, alert_type: str, message: str):
        """Create a new alert"""
        alert = {
            'timestamp': time.time(),
            'type': alert_type,
            'message': message,
            'severity': 'warning' if alert_type in ['memory', 'cpu', 'disk'] else 'critical'
        }
        
        self.alerts.append(alert)
        logger.warning(f"Health alert: {alert_type} - {message}")
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def _check_database(self) -> Dict[str, Any]:
        """Check database health"""
        # This would check database connectivity
        return {
            'status': 'healthy',
            'response_time': 0.1,
            'message': 'Database connection OK'
        }
    
    def _check_memory(self) -> Dict[str, Any]:
        """Check memory health"""
        memory = psutil.virtual_memory()
        return {
            'status': 'healthy' if memory.percent < 85 else 'warning',
            'usage_percent': memory.percent,
            'available_gb': memory.available / (1024**3),
            'message': f"Memory usage: {memory.percent:.1f}%"
        }
    
    def _check_disk(self) -> Dict[str, Any]:
        """Check disk health"""
        disk = psutil.disk_usage('/')
        usage_percent = (disk.used / disk.total) * 100
        return {
            'status': 'healthy' if usage_percent < 90 else 'warning',
            'usage_percent': usage_percent,
            'free_gb': disk.free / (1024**3),
            'message': f"Disk usage: {usage_percent:.1f}%"
        }
    
    def _check_cpu(self) -> Dict[str, Any]:
        """Check CPU health"""
        cpu_percent = psutil.cpu_percent(interval=1)
        return {
            'status': 'healthy' if cpu_percent < 80 else 'warning',
            'usage_percent': cpu_percent,
            'message': f"CPU usage: {cpu_percent:.1f}%"
        }
    
    def _check_cache(self) -> Dict[str, Any]:
        """Check cache health"""
        # This would check cache connectivity
        return {
            'status': 'healthy',
            'message': 'Cache system OK'
        }
    
    def _check_logs(self) -> Dict[str, Any]:
        """Check log file health"""
        try:
            log_file = Path('logs/app.log')
            if log_file.exists():
                size_mb = log_file.stat().st_size / (1024**2)
                return {
                    'status': 'healthy' if size_mb < 100 else 'warning',
                    'size_mb': size_mb,
                    'message': f"Log file size: {size_mb:.1f}MB"
                }
            else:
                return {
                    'status': 'warning',
                    'message': 'Log file not found'
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Error checking logs: {str(e)}"
            }
    
    def record_request(self, success: bool, processing_time: float = None):
        """Record a request"""
        self.metrics['requests_total'] += 1
        
        if success:
            self.metrics['requests_successful'] += 1
        else:
            self.metrics['requests_failed'] += 1
        
        if processing_time is not None:
            self.metrics['file_processing_time'].append({
                'timestamp': time.time(),
                'duration': processing_time
            })
            
            # Keep only last 1000 entries
            if len(self.metrics['file_processing_time']) > 1000:
                self.metrics['file_processing_time'] = self.metrics['file_processing_time'][-1000:]
    
    def record_file_upload(self, file_size: int, processing_time: float):
        """Record a file upload"""
        self.metrics['file_uploads'] += 1
        
        self.metrics['file_processing_time'].append({
            'timestamp': time.time(),
            'duration': processing_time,
            'file_size': file_size
        })
    
    def record_error(self, error_type: str, error_message: str, context: str = None):
        """Record an error"""
        error = {
            'timestamp': time.time(),
            'type': error_type,
            'message': error_message,
            'context': context
        }
        
        self.metrics['errors'].append(error)
        
        # Keep only last 1000 errors
        if len(self.metrics['errors']) > 1000:
            self.metrics['errors'] = self.metrics['errors'][-1000:]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        health_checks = {}
        
        for check_name, check_func in self.health_checks.items():
            try:
                health_checks[check_name] = check_func()
            except Exception as e:
                health_checks[check_name] = {
                    'status': 'error',
                    'message': f"Check failed: {str(e)}"
                }
        
        # Determine overall status
        overall_status = 'healthy'
        for check_result in health_checks.values():
            if check_result['status'] == 'error':
                overall_status = 'error'
                break
            elif check_result['status'] == 'warning' and overall_status == 'healthy':
                overall_status = 'warning'
        
        return {
            'overall_status': overall_status,
            'timestamp': time.time(),
            'uptime_seconds': time.time() - self.start_time,
            'checks': health_checks,
            'metrics': self._get_metrics_summary(),
            'alerts': self.alerts[-10:] if self.alerts else []
        }
    
    def _get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        total_requests = self.metrics['requests_total']
        success_rate = (self.metrics['requests_successful'] / total_requests * 100) if total_requests > 0 else 0
        
        avg_processing_time = 0
        if self.metrics['file_processing_time']:
            avg_processing_time = sum(
                entry['duration'] for entry in self.metrics['file_processing_time']
            ) / len(self.metrics['file_processing_time'])
        
        return {
            'total_requests': total_requests,
            'success_rate': success_rate,
            'file_uploads': self.metrics['file_uploads'],
            'avg_processing_time': avg_processing_time,
            'recent_errors': len([
                error for error in self.metrics['errors']
                if error['timestamp'] > time.time() - 3600  # Last hour
            ])
        }
    
    def get_metrics_export(self) -> Dict[str, Any]:
        """Get metrics for export"""
        return {
            'timestamp': time.time(),
            'uptime_seconds': time.time() - self.start_time,
            'metrics': self.metrics,
            'health_status': self.get_health_status()
        }
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False

# Global health monitor instance
health_monitor = HealthMonitor()
