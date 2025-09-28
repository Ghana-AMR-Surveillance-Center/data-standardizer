"""
Configuration Management Module
Handles application configuration and settings.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import streamlit as st

class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_default_config()
        self._load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            "app": {
                "name": "GLASS Data Standardizer",
                "version": "1.0.0",
                "debug": False,
                "max_file_size_mb": 100,
                "supported_formats": ["csv", "xlsx", "xls"]
            },
            "file_processing": {
                "chunk_size": 10000,
                "max_memory_usage_mb": 500,
                "encoding_detection": True,
                "auto_clean_headers": True
            },
            "data_quality": {
                "completeness_threshold": 0.9,
                "consistency_threshold": 0.8,
                "accuracy_threshold": 0.8,
                "validity_threshold": 0.8,
                "uniqueness_threshold": 0.95
            },
            "export": {
                "default_format": "xlsx",
                "include_validation": True,
                "freeze_header": True,
                "auto_adjust_columns": True
            },
            "ui": {
                "show_progress_bars": True,
                "show_data_previews": True,
                "max_preview_rows": 20,
                "theme": "light"
            },
            "logging": {
                "level": "INFO",
                "log_to_file": True,
                "max_log_files": 10
            }
        }
    
    def _load_config(self):
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    self._merge_config(file_config)
            except Exception as e:
                st.warning(f"Could not load config file: {e}. Using defaults.")
    
    def _merge_config(self, file_config: Dict[str, Any]):
        """Merge file configuration with defaults."""
        def merge_dicts(default: Dict, override: Dict) -> Dict:
            for key, value in override.items():
                if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                    merge_dicts(default[key], value)
                else:
                    default[key] = value
            return default
        
        self.config = merge_dicts(self.config, file_config)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key path."""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Set configuration value by dot-separated key path."""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            st.error(f"Could not save config file: {e}")
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self.config = self._load_default_config()
        self.save_config()
    
    def get_file_size_limit(self) -> int:
        """Get maximum file size limit in bytes."""
        return self.get("app.max_file_size_mb", 100) * 1024 * 1024
    
    def get_supported_formats(self) -> list:
        """Get list of supported file formats."""
        return self.get("app.supported_formats", ["csv", "xlsx", "xls"])
    
    def get_quality_thresholds(self) -> Dict[str, float]:
        """Get data quality thresholds."""
        return {
            "completeness": self.get("data_quality.completeness_threshold", 0.9),
            "consistency": self.get("data_quality.consistency_threshold", 0.8),
            "accuracy": self.get("data_quality.accuracy_threshold", 0.8),
            "validity": self.get("data_quality.validity_threshold", 0.8),
            "uniqueness": self.get("data_quality.uniqueness_threshold", 0.95)
        }
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get("app.debug", False)
    
    def should_show_progress(self) -> bool:
        """Check if progress bars should be shown."""
        return self.get("ui.show_progress_bars", True)
    
    def get_max_preview_rows(self) -> int:
        """Get maximum number of rows to show in previews."""
        return self.get("ui.max_preview_rows", 20)

# Global config instance
config = ConfigManager()

def get_config() -> ConfigManager:
    """Get the global configuration instance."""
    return config
