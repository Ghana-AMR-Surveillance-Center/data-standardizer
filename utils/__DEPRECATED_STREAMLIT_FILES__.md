# Deprecated Streamlit-Only Utility Files

The following utility files contain Streamlit-specific code and are **deprecated**.
They are not used by the Dash application and may be removed in a future version.

## Deprecated Files

- `utils/file_handler.py` - Streamlit file upload UI
- `utils/file_merger.py` - Streamlit file merging UI
- `utils/column_mapper.py` - Streamlit column mapping UI
- `utils/excel_exporter.py` - Streamlit export UI
- `utils/theme.py` - Streamlit theming
- `utils/data_profiler.py` - Streamlit profiling UI
- `utils/data_quality.py` - Streamlit quality assessment UI
- `utils/transformer.py` - Streamlit transformation UI
- `utils/age_transformer.py` - Streamlit age transformation UI
- `utils/error_handler.py` - Streamlit error display
- `utils/logger.py` - Streamlit logging UI
- `utils/performance_monitor.py` - Streamlit performance UI
- `utils/cache_manager.py` - Streamlit cache UI
- `utils/user_feedback.py` - Streamlit feedback UI
- `utils/security.py` - Streamlit security UI

## Migration Notes

The Dash application (`dash_app.py`) implements its own UI components and does not use these Streamlit-specific utilities. Core business logic has been moved to:

- `core/services/` - Core business logic services
- `utils/glass_exporter.py` - GLASS export (framework-agnostic)
- `utils/glass_validator.py` - GLASS validation (framework-agnostic)
- `utils/validator.py` - Data validation (framework-agnostic)

If you need functionality from these deprecated files, please:
1. Check if it's already implemented in `dash_app.py`
2. Check if core logic exists in `core/services/`
3. Create a new framework-agnostic utility if needed

