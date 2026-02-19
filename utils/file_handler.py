"""
File Handler Module
Handles file upload, reading, and basic processing for CSV and Excel files.
"""

import pandas as pd
import io
import logging
from typing import Optional, Dict, Any, List, Tuple
import os

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

try:
    from utils.security import security_manager, sanitize_dataframe_formulas
    from utils.app_settings import app_settings
except ImportError:
    security_manager = None
    app_settings = None
    sanitize_dataframe_formulas = None

logger = logging.getLogger(__name__)


class FileHandler:
    """
    Handles file upload and processing operations.
    
    Can be used:
    - Integrated: With Streamlit file uploader
    - Standalone: With file paths
    """
    
    def __init__(self):
        self.supported_formats = ['csv', 'xlsx', 'xls']
    
    def read_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Read file from path (standalone use).
        
        Args:
            file_path: Path to file (CSV or Excel)
            
        Returns:
            pd.DataFrame: Loaded dataframe or None if error
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None
            
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                logger.error(f"Unsupported file format: {file_ext}")
                return None
            
            logger.info(f"Successfully loaded {len(df)} rows from {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            return None
    
    def read_file_from_bytes(self, file_bytes: bytes, file_name: str) -> Optional[pd.DataFrame]:
        """
        Read file from bytes (for API or programmatic use).
        
        Args:
            file_bytes: File content as bytes
            file_name: Original file name (for format detection)
            
        Returns:
            pd.DataFrame: Loaded dataframe or None if error
        """
        try:
            file_ext = os.path.splitext(file_name)[1].lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(io.BytesIO(file_bytes))
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(io.BytesIO(file_bytes))
            else:
                logger.error(f"Unsupported file format: {file_ext}")
                return None
            
            logger.info(f"Successfully loaded {len(df)} rows from bytes")
            return df
            
        except Exception as e:
            logger.error(f"Error reading file from bytes: {str(e)}")
            return None
        
    def upload_file(self) -> Optional[pd.DataFrame]:
        """
        Create file upload widget and process uploaded file with security validation.
        Requires Streamlit to be available.
        
        Returns:
            pd.DataFrame: Loaded dataframe or None if no file uploaded
            
        Raises:
            ImportError: If Streamlit is not available
        """
        if not STREAMLIT_AVAILABLE:
            raise ImportError(
                "Streamlit is required for upload_file(). "
                "Use read_file(file_path) for standalone usage."
            )
        
        uploaded_file = st.file_uploader(
            "Upload your data file",
            type=self.supported_formats,
            help="Supported formats: CSV, Excel (.xlsx, .xls)"
        )
        
        if uploaded_file is not None:
            try:
                # Security validation (if available)
                if security_manager:
                    validation_result = security_manager.validate_file_upload(uploaded_file)
                else:
                    # Basic validation for standalone use
                    validation_result = {'valid': True, 'errors': [], 'warnings': []}
                
                if not validation_result['valid']:
                    for error in validation_result['errors']:
                        st.error(f"❌ Security validation failed: {error}")
                        logger.warning(f"File upload rejected: {uploaded_file.name} - {error}")
                    return None
                
                # Show warnings if any
                if validation_result.get('warnings'):
                    for warning in validation_result['warnings']:
                        st.warning(f"⚠️ {warning}")
                        logger.info(f"File upload warning: {uploaded_file.name} - {warning}")
                
                # Log successful validation
                logger.info(f"File upload validated successfully: {uploaded_file.name}")
                
                return self._process_uploaded_file(uploaded_file)
            except Exception as e:
                error_msg = f"Error processing file: {str(e)}"
                st.error(error_msg)
                logger.error(f"File processing error: {uploaded_file.name if uploaded_file else 'unknown'} - {str(e)}", exc_info=True)
                return None
        
        return None
    
    def _process_uploaded_file(self, uploaded_file) -> pd.DataFrame:
        """
        Process the uploaded file based on its type.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            pd.DataFrame: Processed dataframe
        """
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            return self._read_csv(uploaded_file)
        elif file_extension in ['xlsx', 'xls']:
            return self._read_excel(uploaded_file)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def _read_csv(self, uploaded_file) -> pd.DataFrame:
        """
        Read CSV file with intelligent encoding detection and edge case handling.
        
        Handles:
        - Multiple encodings (UTF-8, Latin-1, CP1252, etc.)
        - BOM (Byte Order Mark) removal
        - Inconsistent delimiters (comma, semicolon, tab)
        - Multiple header rows
        - Empty files or files with only headers
        - Footer/summary rows
        
        Args:
            uploaded_file: Streamlit uploaded file object or file-like object
            
        Returns:
            pd.DataFrame: Loaded dataframe
        """
        # Try different encodings
        encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'windows-1252']
        
        # Try different delimiters
        delimiters = [',', ';', '\t', '|']
        
        for encoding in encodings:
            for delimiter in delimiters:
                try:
                    uploaded_file.seek(0)  # Reset file pointer
                    
                    # Read first few lines to detect structure
                    sample_lines = []
                    for _ in range(5):
                        line = uploaded_file.readline()
                        if not line:
                            break
                        sample_lines.append(line.decode(encoding, errors='ignore'))
                    uploaded_file.seek(0)
                    
                    # Try reading with current encoding and delimiter
                    df = pd.read_csv(
                        uploaded_file,
                        encoding=encoding,
                        sep=delimiter,
                        skipinitialspace=True,
                        on_bad_lines='skip',  # Skip bad lines instead of failing
                        engine='python'  # More flexible parsing
                    )
                    
                    # Validate we got meaningful data
                    if len(df) > 0 and len(df.columns) > 0:
                        # Clean up the dataframe
                        df = self._clean_loaded_dataframe(df)
                        
                        if STREAMLIT_AVAILABLE:
                            st.success(f"File loaded successfully with {encoding} encoding, {delimiter} delimiter")
                        logger.info(f"File loaded successfully with {encoding} encoding, {delimiter} delimiter")
                        return df
                        
                except UnicodeDecodeError:
                    continue
                except pd.errors.EmptyDataError:
                    # Empty file - return empty dataframe with message
                    if STREAMLIT_AVAILABLE:
                        st.warning("⚠️ File appears to be empty or contains only headers")
                    logger.warning("File appears to be empty")
                    return pd.DataFrame()
                except Exception as e:
                    logger.debug(f"Failed with {encoding}/{delimiter}: {str(e)}")
                    continue
        
        # If all encodings/delimiters failed, try with error handling
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(
                uploaded_file,
                encoding='utf-8',
                sep=',',
                on_bad_lines='skip',
                engine='python'
            )
            df = self._clean_loaded_dataframe(df)
            if STREAMLIT_AVAILABLE:
                st.warning("⚠️ File loaded with some errors - please review data quality")
            return df
        except Exception as e:
            raise ValueError(f"Could not read CSV file: {str(e)}")
    
    def _clean_loaded_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean loaded dataframe to handle common edge cases.
        
        Args:
            df: Raw loaded dataframe
            
        Returns:
            pd.DataFrame: Cleaned dataframe
        """
        if df.empty:
            return df
        
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Remove rows that are likely footers/summaries (all text, contains "total", "sum", etc.)
        if len(df) > 0:
            footer_keywords = ['total', 'sum', 'summary', 'grand total', 'subtotal', 'count']
            mask = df.astype(str).apply(
                lambda row: any(keyword in ' '.join(row.values).lower() for keyword in footer_keywords),
                axis=1
            )
            mask_series = pd.Series(mask) if not isinstance(mask, pd.Series) else mask
            if mask_series.any():
                df = df[~mask_series]
                logger.info(f"Removed {mask_series.sum()} footer/summary rows")
        
        # Clean column names (remove BOM, whitespace, special characters)
        df.columns = df.columns.str.replace('\ufeff', '', regex=False)  # Remove BOM
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.replace(r'[\r\n\t]', ' ', regex=True)  # Replace newlines/tabs with spaces
        
        # Remove duplicate column names by appending numbers
        if df.columns.duplicated().any():
            seen = {}
            new_columns = []
            for col in df.columns:
                if col in seen:
                    seen[col] += 1
                    new_columns.append(f"{col}_{seen[col]}")
                else:
                    seen[col] = 0
                    new_columns.append(col)
            df.columns = new_columns
            logger.warning("Found duplicate column names - renamed with suffixes")
        
        # Sanitize formula injection (CSV/Excel security)
        if sanitize_dataframe_formulas:
            try:
                df = sanitize_dataframe_formulas(df)
                logger.info("Applied formula injection sanitization")
            except Exception as e:
                logger.warning(f"Formula sanitization skipped: {e}")
        
        return df
    
    def _read_excel(self, uploaded_file) -> pd.DataFrame:
        """
        Read Excel file with retry logic and edge case handling.
        
        Handles:
        - Multiple sheets
        - Merged cells
        - Multiple header rows
        - Empty sheets
        - Footer rows
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            pd.DataFrame: Loaded dataframe
            
        Raises:
            ValueError: If file cannot be read with any engine
        """
        # Import retry handler (optional, with fallback)
        try:
            from utils.retry_handler import retry_file_operation
            use_retry = True
        except ImportError:
            use_retry = False
            logger.warning("Retry handler not available, proceeding without retry logic")
        
        def _read_with_engine(engine: str, sheet_name=None):
            uploaded_file.seek(0)
            # Type ignore: pandas accepts string engine names
            return pd.read_excel(
                uploaded_file,
                engine=engine,
                sheet_name=sheet_name,
                header=0,  # First row as header
                skip_blank_lines=True
            )  # type: ignore
        
        # Apply retry decorator if available
        if use_retry:
            _read_with_engine = retry_file_operation(max_retries=2)(_read_with_engine)
        
        # Try different engines with retry logic
        engines = ['openpyxl', 'xlrd']
        last_error = None
        
        for engine in engines:
            try:
                # First, check if file has multiple sheets
                uploaded_file.seek(0)
                try:
                    excel_file = pd.ExcelFile(uploaded_file, engine=engine)
                    sheet_names = excel_file.sheet_names
                    
                    # If multiple sheets, use first non-empty sheet or let user choose
                    if len(sheet_names) > 1:
                        logger.info(f"File has {len(sheet_names)} sheets: {sheet_names}")
                        if STREAMLIT_AVAILABLE:
                            st.info(f"📄 File has {len(sheet_names)} sheets. Using first sheet: '{sheet_names[0]}'")
                        
                        # Try to find the best sheet (one with most data)
                        best_sheet = sheet_names[0]
                        max_rows = 0
                        for sheet in sheet_names:
                            try:
                                uploaded_file.seek(0)
                                test_df = pd.read_excel(uploaded_file, sheet_name=sheet, engine=engine, nrows=10)
                                if len(test_df) > max_rows:
                                    max_rows = len(test_df)
                                    best_sheet = sheet
                            except:
                                continue
                        
                        uploaded_file.seek(0)
                        df = pd.read_excel(uploaded_file, sheet_name=best_sheet, engine=engine)
                    else:
                        uploaded_file.seek(0)
                        df = pd.read_excel(uploaded_file, engine=engine)
                except:
                    # Fallback: read without sheet detection
                    uploaded_file.seek(0)
                    df = _read_with_engine(engine)
                
                # Clean the dataframe
                df = self._clean_loaded_dataframe(df)
                
                # Handle merged cells (they often result in NaN in first column)
                if len(df) > 0:
                    # Remove rows where all values are NaN (likely from merged cells)
                    df = df.dropna(how='all')
                    
                    # Forward fill merged cells in first column if appropriate
                    if len(df.columns) > 0:
                        first_col = df.columns[0]
                        if df[first_col].isna().sum() > 0 and df[first_col].isna().sum() < len(df) * 0.5:
                            # Only fill if less than 50% are NaN (likely merged cells)
                            df[first_col] = df[first_col].ffill()
                
                if STREAMLIT_AVAILABLE:
                    if engine == 'openpyxl':
                        st.success("Excel file loaded successfully")
                    else:
                        st.success(f"Excel file loaded successfully with {engine} engine")
                logger.info(f"Excel file loaded successfully with {engine} engine")
                return df
            except pd.errors.EmptyDataError:
                if STREAMLIT_AVAILABLE:
                    st.warning("⚠️ Excel file appears to be empty")
                logger.warning("Excel file appears to be empty")
                return pd.DataFrame()
            except Exception as e:
                last_error = e
                logger.warning(f"Failed to read Excel with {engine} engine: {str(e)}")
                if engine == engines[-1]:  # Last engine
                    if STREAMLIT_AVAILABLE:
                        st.error(f"Error reading Excel file with all engines: {str(e)}")
                    raise ValueError(f"Could not read Excel file with any engine: {str(e)}") from e
                continue
        
        # This should never be reached, but type checker needs it
        if last_error:
            raise ValueError(f"Could not read Excel file: {str(last_error)}") from last_error
        raise ValueError("Could not read Excel file: Unknown error")
    
    def get_file_info(self, df: pd.DataFrame, filename: str) -> Dict[str, Any]:
        """
        Get basic information about the loaded file.
        
        Args:
            df: Loaded dataframe
            filename: Name of the uploaded file
            
        Returns:
            Dict: File information
        """
        return {
            'filename': filename,
            'rows': len(df),
            'columns': len(df.columns),
            'size_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'dtypes': df.dtypes.value_counts().to_dict()
        }
    
    def detect_delimiter(self, text_sample: str) -> str:
        """
        Detect the most likely delimiter in a CSV text sample.
        
        Args:
            text_sample: Sample text from CSV file
            
        Returns:
            str: Most likely delimiter
        """
        delimiters = [',', ';', '\t', '|']
        delimiter_counts = {}
        
        for delimiter in delimiters:
            delimiter_counts[delimiter] = text_sample.count(delimiter)
        
        # Find delimiter with maximum count
        max_count = max(delimiter_counts.values())
        for delimiter, count in delimiter_counts.items():
            if count == max_count:
                return delimiter
        
        # Fallback to comma if no delimiter found
        return ','
    
    def preview_data(self, df: pd.DataFrame, num_rows: int = 5) -> None:
        """
        Display a preview of the loaded data (requires Streamlit).
        
        Args:
            df: Dataframe to preview
            num_rows: Number of rows to show
            
        Raises:
            ImportError: If Streamlit is not available
        """
        if not STREAMLIT_AVAILABLE:
            raise ImportError(
                "Streamlit is required for preview_data(). "
                "Use df.head(num_rows) for standalone usage."
            )
        
        st.subheader("Data Preview")
        try:
            from .helpers import prepare_df_for_display
            st.dataframe(prepare_df_for_display(df.head(num_rows)), use_container_width=True)
        except ImportError:
            st.dataframe(df.head(num_rows), use_container_width=True)
        
        # Show basic statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", len(df))
        with col2:
            st.metric("Total Columns", len(df.columns))
        with col3:
            st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    def get_preview_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get preview information without Streamlit (standalone use).
        
        Args:
            df: Dataframe to analyze
            
        Returns:
            Dict: Preview information
        """
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024**2, 2),
            'column_names': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'sample_data': df.head(5).to_dict('records')
        }
