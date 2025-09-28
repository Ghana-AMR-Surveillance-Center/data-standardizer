"""
Application configuration management
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import streamlit as st

class AppConfig:
    """Centralized application configuration management."""
    
    def __init__(self):
        self.config_file = Path("config.json")
        self.default_config = self._get_default_config()
        self.config = self._load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "app": {
                "name": "GLASS Data Standardizer",
                "version": "2.0.0",
                "debug": False,
                "max_file_size_mb": 100,
                "max_files": 10
            },
            "ui": {
                "theme": "light",
                "sidebar_state": "expanded",
                "page_title": "GLASS Data Standardizer",
                "page_icon": "🏥"
            },
            "data_processing": {
                "chunk_size": 10000,
                "max_memory_usage_mb": 500,
                "enable_optimization": True,
                "auto_detect_types": True
            },
            "file_formats": {
                "supported_csv": [".csv", ".tsv"],
                "supported_excel": [".xlsx", ".xls"],
                "max_excel_sheets": 20
            },
            "merging": {
                "similarity_threshold": 0.5,
                "auto_map_threshold": 0.8,
                "enable_smart_mapping": True,
                "remove_duplicates": True
            },
            "export": {
                "default_format": "csv",
                "include_metadata": True,
                "compression": False
            },
            "logging": {
                "level": "INFO",
                "max_log_size_mb": 10,
                "backup_count": 5
            }
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_configs(self.default_config, loaded_config)
            except Exception as e:
                st.warning(f"Failed to load config: {e}. Using defaults.")
                return self.default_config.copy()
        else:
            self.save_config(self.default_config)
            return self.default_config.copy()
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Recursively merge loaded config with defaults."""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self, config: Optional[Dict] = None):
        """Save configuration to file."""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            st.error(f"Failed to save config: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation."""
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        self.save_config()
    
    def get_file_size_limit(self) -> int:
        """Get maximum file size in bytes."""
        return self.get("app.max_file_size_mb", 100) * 1024 * 1024
    
    def get_max_files(self) -> int:
        """Get maximum number of files allowed."""
        return self.get("app.max_files", 10)
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get("app.debug", False)
    
    def get_supported_formats(self) -> Dict[str, list]:
        """Get supported file formats."""
        return {
            'csv': self.get("file_formats.supported_csv", [".csv", ".tsv"]),
            'excel': self.get("file_formats.supported_excel", [".xlsx", ".xls"])
        }
    
    def get_merging_config(self) -> Dict[str, Any]:
        """Get merging configuration."""
        return {
            'similarity_threshold': self.get("merging.similarity_threshold", 0.5),
            'auto_map_threshold': self.get("merging.auto_map_threshold", 0.8),
            'enable_smart_mapping': self.get("merging.enable_smart_mapping", True),
            'remove_duplicates': self.get("merging.remove_duplicates", True)
        }
    
    def get_data_processing_config(self) -> Dict[str, Any]:
        """Get data processing configuration."""
        return {
            'chunk_size': self.get("data_processing.chunk_size", 10000),
            'max_memory_usage_mb': self.get("data_processing.max_memory_usage_mb", 500),
            'enable_optimization': self.get("data_processing.enable_optimization", True),
            'auto_detect_types': self.get("data_processing.auto_detect_types", True)
        }
    
    def show_config_editor(self):
        """Show configuration editor in Streamlit."""
        st.markdown("### ⚙️ Configuration Settings")
        
        with st.expander("App Settings", expanded=True):
            debug_mode = st.checkbox("Debug Mode", value=self.get("app.debug", False))
            max_file_size = st.number_input("Max File Size (MB)", value=self.get("app.max_file_size_mb", 100), min_value=1, max_value=1000)
            max_files = st.number_input("Max Files", value=self.get("app.max_files", 10), min_value=1, max_value=50)
            
            if st.button("Save App Settings"):
                self.set("app.debug", debug_mode)
                self.set("app.max_file_size_mb", max_file_size)
                self.set("app.max_files", max_files)
                st.success("App settings saved!")
        
        with st.expander("Data Processing Settings", expanded=False):
            chunk_size = st.number_input("Chunk Size", value=self.get("data_processing.chunk_size", 10000), min_value=1000, max_value=100000)
            max_memory = st.number_input("Max Memory Usage (MB)", value=self.get("data_processing.max_memory_usage_mb", 500), min_value=100, max_value=2000)
            enable_optimization = st.checkbox("Enable Optimization", value=self.get("data_processing.enable_optimization", True))
            
            if st.button("Save Data Processing Settings"):
                self.set("data_processing.chunk_size", chunk_size)
                self.set("data_processing.max_memory_usage_mb", max_memory)
                self.set("data_processing.enable_optimization", enable_optimization)
                st.success("Data processing settings saved!")
        
        with st.expander("Merging Settings", expanded=False):
            similarity_threshold = st.slider("Similarity Threshold", 0.0, 1.0, value=self.get("merging.similarity_threshold", 0.5), step=0.1)
            auto_map_threshold = st.slider("Auto Map Threshold", 0.0, 1.0, value=self.get("merging.auto_map_threshold", 0.8), step=0.1)
            enable_smart_mapping = st.checkbox("Enable Smart Mapping", value=self.get("merging.enable_smart_mapping", True))
            
            if st.button("Save Merging Settings"):
                self.set("merging.similarity_threshold", similarity_threshold)
                self.set("merging.auto_map_threshold", auto_map_threshold)
                self.set("merging.enable_smart_mapping", enable_smart_mapping)
                st.success("Merging settings saved!")

# Global config instance
app_config = AppConfig()
