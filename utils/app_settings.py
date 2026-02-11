"""
Enhanced application settings and configuration management
"""

import streamlit as st
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AppSettings:
    """
    Enhanced application settings management
    """
    
    def __init__(self):
        self.settings_file = Path("app_settings.json")
        self.default_settings = self._get_default_settings()
        self.settings = self._load_settings()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default application settings"""
        return {
            "ui": {
                "theme": "light",
                "sidebar_state": "expanded",
                "page_width": "wide",
                "show_help_tooltips": True,
                "show_progress_bars": True,
                "animation_speed": "normal"
            },
            "data_processing": {
                "max_file_size_mb": 100,
                "chunk_size": 1000,
                "memory_limit_mb": 2048,
                "auto_optimize_dataframes": True,
                "cache_enabled": True,
                "cache_duration_minutes": 30
            },
            "amr_analysis": {
                "clsi_version": "M100-S33",
                "confidence_threshold": 0.8,
                "min_samples_for_analysis": 10,
                "show_confidence_intervals": True,
                "export_high_resolution": True,
                "default_chart_theme": "plotly_white"
            },
            "file_handling": {
                "supported_formats": ["csv", "xlsx", "xls"],
                "auto_detect_encoding": True,
                "backup_original_files": True,
                "compress_exports": True
            },
            "performance": {
                "enable_monitoring": True,
                "log_performance_metrics": True,
                "optimize_memory_usage": True,
                "parallel_processing": True
            },
            "notifications": {
                "show_success_messages": True,
                "show_warning_messages": True,
                "auto_dismiss_duration": 5,
                "show_operation_status": True
            }
        }
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create default"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                
                # Merge with defaults to ensure all keys exist
                settings = self.default_settings.copy()
                settings.update(loaded_settings)
                return settings
            except Exception as e:
                logger.warning(f"Failed to load settings: {e}. Using defaults.")
                return self.default_settings.copy()
        else:
            # Create default settings file
            self._save_settings(self.default_settings)
            return self.default_settings.copy()
    
    def _save_settings(self, settings: Dict[str, Any]):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get setting value using dot notation (e.g., 'ui.theme')"""
        keys = key_path.split('.')
        value = self.settings
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Set setting value using dot notation"""
        keys = key_path.split('.')
        settings = self.settings
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in settings:
                settings[key] = {}
            settings = settings[key]
        
        # Set the value
        settings[keys[-1]] = value
        
        # Save to file
        self._save_settings(self.settings)
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.default_settings.copy()
        self._save_settings(self.settings)
        logger.info("Settings reset to defaults")
    
    def show_settings_ui(self):
        """Show settings UI in sidebar"""
        with st.sidebar.expander("⚙️ Settings", expanded=False):
            # UI Settings
            st.subheader("🎨 Interface")
            
            theme = st.selectbox(
                "Theme",
                ["light", "dark"],
                index=0 if self.get("ui.theme") == "light" else 1
            )
            self.set("ui.theme", theme)
            
            show_tooltips = st.checkbox(
                "Show Help Tooltips",
                value=self.get("ui.show_help_tooltips", True)
            )
            self.set("ui.show_help_tooltips", show_tooltips)
            
            show_progress = st.checkbox(
                "Show Progress Bars",
                value=self.get("ui.show_progress_bars", True)
            )
            self.set("ui.show_progress_bars", show_progress)
            
            # Data Processing Settings
            st.subheader("📊 Data Processing")
            
            max_file_size = st.number_input(
                "Max File Size (MB)",
                min_value=10,
                max_value=1000,
                value=self.get("data_processing.max_file_size_mb", 100)
            )
            self.set("data_processing.max_file_size_mb", max_file_size)
            
            auto_optimize = st.checkbox(
                "Auto-optimize DataFrames",
                value=self.get("data_processing.auto_optimize_dataframes", True)
            )
            self.set("data_processing.auto_optimize_dataframes", auto_optimize)
            
            cache_enabled = st.checkbox(
                "Enable Caching",
                value=self.get("data_processing.cache_enabled", True)
            )
            self.set("data_processing.cache_enabled", cache_enabled)
            
            # AMR Analysis Settings
            st.subheader("🧬 AMR Analysis")
            
            clsi_version = st.selectbox(
                "CLSI Version",
                ["M100-S33", "M100-S32", "M100-S31"],
                index=0 if self.get("amr_analysis.clsi_version") == "M100-S33" else 1
            )
            self.set("amr_analysis.clsi_version", clsi_version)
            
            confidence_threshold = st.slider(
                "Confidence Threshold",
                min_value=0.1,
                max_value=1.0,
                value=self.get("amr_analysis.confidence_threshold", 0.8),
                step=0.1
            )
            self.set("amr_analysis.confidence_threshold", confidence_threshold)
            
            min_samples = st.number_input(
                "Min Samples for Analysis",
                min_value=1,
                max_value=100,
                value=self.get("amr_analysis.min_samples_for_analysis", 10)
            )
            self.set("amr_analysis.min_samples_for_analysis", min_samples)
            
            # Performance Settings
            st.subheader("⚡ Performance")
            
            enable_monitoring = st.checkbox(
                "Enable Performance Monitoring",
                value=self.get("performance.enable_monitoring", True)
            )
            self.set("performance.enable_monitoring", enable_monitoring)
            
            optimize_memory = st.checkbox(
                "Optimize Memory Usage",
                value=self.get("performance.optimize_memory_usage", True)
            )
            self.set("performance.optimize_memory_usage", optimize_memory)
            
            # Reset button
            st.markdown("---")
            if st.button("🔄 Reset to Defaults", use_container_width=True):
                self.reset_to_defaults()
                st.rerun()
    
    def get_file_size_limit(self) -> int:
        """Get file size limit in bytes"""
        return self.get("data_processing.max_file_size_mb", 100) * 1024 * 1024
    
    def is_caching_enabled(self) -> bool:
        """Check if caching is enabled"""
        return self.get("data_processing.cache_enabled", True)
    
    def get_cache_duration(self) -> int:
        """Get cache duration in seconds"""
        return self.get("data_processing.cache_duration_minutes", 30) * 60
    
    def should_optimize_dataframes(self) -> bool:
        """Check if DataFrame optimization should be enabled"""
        return self.get("data_processing.auto_optimize_dataframes", True)
    
    def get_amr_confidence_threshold(self) -> float:
        """Get AMR analysis confidence threshold"""
        return self.get("amr_analysis.confidence_threshold", 0.8)
    
    def get_min_samples_for_analysis(self) -> int:
        """Get minimum samples required for analysis"""
        return self.get("amr_analysis.min_samples_for_analysis", 10)

# Global settings instance
app_settings = AppSettings()
