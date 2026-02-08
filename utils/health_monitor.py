"""
Health monitoring system for production deployment
"""

import logging
import psutil
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import sys

logger = logging.getLogger(__name__)


class HealthMonitor:
    """Monitor application and system health"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.start_time = datetime.now()
        self.metrics = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_failed': 0,
            'errors_total': 0,
            'processing_times': []
        }
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'error_rate': 0.1  # 10% error rate
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_mb': memory.available / (1024 * 1024),
                    'disk_percent': disk.percent,
                    'disk_free_gb': disk.free / (1024 * 1024 * 1024)
                },
                'application': {
                    'requests_total': self.metrics['requests_total'],
                    'requests_success': self.metrics['requests_success'],
                    'requests_failed': self.metrics['requests_failed'],
                    'errors_total': self.metrics['errors_total'],
                    'avg_processing_time': self._calculate_avg_processing_time()
                },
                'warnings': self._check_thresholds(cpu_percent, memory.percent, disk.percent)
            }
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _check_thresholds(self, cpu: float, memory: float, disk: float) -> list:
        """Check if any metrics exceed thresholds"""
        warnings = []
        
        if cpu > self.thresholds['cpu_percent']:
            warnings.append(f"High CPU usage: {cpu:.1f}%")
        
        if memory > self.thresholds['memory_percent']:
            warnings.append(f"High memory usage: {memory:.1f}%")
        
        if disk > self.thresholds['disk_percent']:
            warnings.append(f"High disk usage: {disk:.1f}%")
        
        # Check error rate
        if self.metrics['requests_total'] > 0:
            error_rate = self.metrics['requests_failed'] / self.metrics['requests_total']
            if error_rate > self.thresholds['error_rate']:
                warnings.append(f"High error rate: {error_rate:.1%}")
        
        return warnings
    
    def _calculate_avg_processing_time(self) -> float:
        """Calculate average processing time"""
        if not self.metrics['processing_times']:
            return 0.0
        return sum(self.metrics['processing_times']) / len(self.metrics['processing_times'])
    
    def record_request(self, success: bool, processing_time: float = 0.0):
        """Record a request"""
        self.metrics['requests_total'] += 1
        if success:
            self.metrics['requests_success'] += 1
        else:
            self.metrics['requests_failed'] += 1
        
        if processing_time > 0:
            self.metrics['processing_times'].append(processing_time)
            # Keep only last 1000 processing times
            if len(self.metrics['processing_times']) > 1000:
                self.metrics['processing_times'] = self.metrics['processing_times'][-1000:]
    
    def record_error(self):
        """Record an error"""
        self.metrics['errors_total'] += 1
    
    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        health = self.get_system_health()
        
        if health['status'] != 'healthy':
            return False
        
        # Check if any warnings indicate critical issues
        warnings = health.get('warnings', [])
        critical_warnings = [w for w in warnings if 'error rate' in w.lower() or 
                           any(threshold in w.lower() for threshold in ['90%', '95%', '100%'])]
        
        return len(critical_warnings) == 0
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for display"""
        health = self.get_system_health()
        
        return {
            'status': '✅ Healthy' if self.is_healthy() else '⚠️ Degraded',
            'uptime': self._format_uptime(health.get('uptime_seconds', 0)),
            'system': {
                'cpu': f"{health['system']['cpu_percent']:.1f}%",
                'memory': f"{health['system']['memory_percent']:.1f}%",
                'disk': f"{health['system']['disk_percent']:.1f}%"
            },
            'application': {
                'total_requests': health['application']['requests_total'],
                'success_rate': self._calculate_success_rate(),
                'avg_processing_time': f"{health['application']['avg_processing_time']:.2f}s"
            },
            'warnings': health.get('warnings', [])
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime as human-readable string"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def _calculate_success_rate(self) -> str:
        """Calculate success rate percentage"""
        if self.metrics['requests_total'] == 0:
            return "N/A"
        
        rate = (self.metrics['requests_success'] / self.metrics['requests_total']) * 100
        return f"{rate:.1f}%"
    
    def reset_metrics(self):
        """Reset all metrics (useful for testing)"""
        self.metrics = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_failed': 0,
            'errors_total': 0,
            'processing_times': []
        }

# Global health monitor instance
health_monitor = HealthMonitor()
