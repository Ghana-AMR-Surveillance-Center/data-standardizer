"""
Performance monitoring and optimization utilities
"""

import time
import psutil
import pandas as pd
from typing import Dict, Any, Optional
import streamlit as st
from functools import wraps

class PerformanceMonitor:
    """Monitor and optimize application performance."""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = time.time()
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            'percent': process.memory_percent()
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
            'memory_available_gb': psutil.virtual_memory().available / 1024 / 1024 / 1024,
            'disk_usage_percent': psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else 0
        }
    
    def monitor_dataframe_operation(self, operation_name: str):
        """Decorator to monitor DataFrame operations."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = self.get_memory_usage()
                
                try:
                    result = func(*args, **kwargs)
                    
                    end_time = time.time()
                    end_memory = self.get_memory_usage()
                    
                    # Store metrics
                    self.metrics[operation_name] = {
                        'execution_time': end_time - start_time,
                        'memory_delta_mb': end_memory['rss_mb'] - start_memory['rss_mb'],
                        'peak_memory_mb': end_memory['rss_mb'],
                        'success': True
                    }
                    
                    return result
                    
                except Exception as e:
                    end_time = time.time()
                    self.metrics[operation_name] = {
                        'execution_time': end_time - start_time,
                        'memory_delta_mb': 0,
                        'peak_memory_mb': start_memory['rss_mb'],
                        'success': False,
                        'error': str(e)
                    }
                    raise
            
            return wrapper
        return decorator
    
    def optimize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize DataFrame for better performance."""
        original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
        
        # Convert object columns to appropriate types
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try to convert to numeric
                try:
                    numeric_series = pd.to_numeric(df[col], errors='coerce')
                    if not numeric_series.isna().all():
                        df[col] = numeric_series
                        continue
                except:
                    pass
                
                # Try to convert to datetime
                try:
                    datetime_series = pd.to_datetime(df[col], errors='coerce')
                    if not datetime_series.isna().all():
                        df[col] = datetime_series
                        continue
                except:
                    pass
                
                # Convert to category if low cardinality
                if df[col].nunique() / len(df) < 0.5:
                    df[col] = df[col].astype('category')
        
        optimized_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
        memory_saved = original_memory - optimized_memory
        
        if memory_saved > 1:  # Only log if we saved more than 1MB
            st.info(f"💾 Memory optimization: Saved {memory_saved:.1f}MB ({memory_saved/original_memory*100:.1f}%)")
        
        return df
    
    def show_performance_summary(self):
        """Show performance summary to user."""
        if not self.metrics:
            return
        
        with st.expander("📊 Performance Summary", expanded=False):
            st.markdown("### Operation Performance")
            
            for operation, metrics in self.metrics.items():
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Operation", operation)
                
                with col2:
                    st.metric("Time (s)", f"{metrics['execution_time']:.2f}")
                
                with col3:
                    st.metric("Memory (MB)", f"{metrics['peak_memory_mb']:.1f}")
                
                with col4:
                    status = "✅" if metrics['success'] else "❌"
                    st.metric("Status", status)
            
            # System information
            st.markdown("### System Information")
            system_info = self.get_system_info()
            memory_info = self.get_memory_usage()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("CPU Cores", system_info['cpu_count'])
            
            with col2:
                st.metric("Memory Used", f"{memory_info['percent']:.1f}%")
            
            with col3:
                st.metric("Available Memory", f"{system_info['memory_available_gb']:.1f}GB")

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
