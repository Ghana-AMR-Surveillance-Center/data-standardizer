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
        """Optimize DataFrame for better performance with improved type inference."""
        if df.empty:
            return df
        
        original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
        df = df.copy()  # Work on a copy to avoid side effects
        
        # Convert object columns to appropriate types
        for col in df.columns:
            # Skip category columns - they're already optimized
            if pd.api.types.is_categorical_dtype(df[col]):
                continue
                
            if df[col].dtype == 'object':
                # Skip if column is mostly empty
                null_ratio = df[col].isna().sum() / len(df)
                if null_ratio > 0.9:
                    continue
                
                # Try to convert to numeric (check if majority are numeric)
                # But skip if column name suggests it's categorical (e.g., "type", "category", "status")
                categorical_keywords = ['type', 'category', 'status', 'specimen', 'organism', 'antibiotic', 'result']
                is_likely_categorical = any(keyword in col.lower() for keyword in categorical_keywords)
                
                if not is_likely_categorical:
                    try:
                        numeric_series = pd.to_numeric(df[col], errors='coerce')
                        # Type check: pd.to_numeric returns Series for Series input
                        if isinstance(numeric_series, pd.Series):
                            numeric_count = numeric_series.notna().sum()  # type: ignore
                            if numeric_count > len(df) * 0.5:  # More than 50% numeric
                                df[col] = numeric_series
                                continue
                    except Exception:
                        pass
                
                # Try to convert to datetime (check if majority are dates)
                try:
                    datetime_series = pd.to_datetime(df[col], errors='coerce')
                    datetime_count = datetime_series.notna().sum()
                    if datetime_count > len(df) * 0.5:  # More than 50% dates
                        df[col] = datetime_series
                        continue
                except Exception:
                    pass
                
                # Convert to category if low cardinality (improved threshold)
                # Only for columns that are likely categorical
                unique_ratio = df[col].nunique() / len(df)
                if (unique_ratio < 0.5 and df[col].nunique() < 10000) or is_likely_categorical:  # Reasonable limit
                    try:
                        df[col] = df[col].astype('category')
                    except Exception:
                        pass
        
        # Optimize integer columns (downcast to smaller int types)
        for col in df.select_dtypes(include=['int64']).columns:
            try:
                df[col] = pd.to_numeric(df[col], downcast='integer')
            except Exception:
                pass
        
        # Optimize float columns (downcast to float32 if precision allows)
        for col in df.select_dtypes(include=['float64']).columns:
            try:
                # Check if float32 precision is sufficient
                float32_series = df[col].astype('float32')
                if (df[col] - float32_series).abs().max() < 1e-6:
                    df[col] = float32_series
            except Exception:
                pass
        
        optimized_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
        memory_saved = original_memory - optimized_memory
        
        if memory_saved > 1:  # Only log if we saved more than 1MB
            percent_saved = (memory_saved / original_memory * 100) if original_memory > 0 else 0
            st.info(f"💾 Memory optimization: Saved {memory_saved:.1f}MB ({percent_saved:.1f}%)")
        
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
