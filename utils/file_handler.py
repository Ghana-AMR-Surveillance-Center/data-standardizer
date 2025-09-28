"""
File Handler Module
Handles file upload, reading, and basic processing for CSV and Excel files.
"""

import pandas as pd
import streamlit as st
import io
from typing import Optional, Dict, Any, List, Tuple


class FileHandler:
    """Handles file upload and processing operations."""
    
    def __init__(self):
        self.supported_formats = ['csv', 'xlsx', 'xls']
        
    def upload_file(self) -> Optional[pd.DataFrame]:
        """
        Create file upload widget and process uploaded file.
        
        Returns:
            pd.DataFrame: Loaded dataframe or None if no file uploaded
        """
        uploaded_file = st.file_uploader(
            "Upload your data file",
            type=self.supported_formats,
            help="Supported formats: CSV, Excel (.xlsx, .xls)"
        )
        
        if uploaded_file is not None:
            try:
                return self._process_uploaded_file(uploaded_file)
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
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
        Read CSV file with intelligent encoding detection.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            pd.DataFrame: Loaded dataframe
        """
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                uploaded_file.seek(0)  # Reset file pointer
                df = pd.read_csv(uploaded_file, encoding=encoding)
                st.success(f"File loaded successfully with {encoding} encoding")
                return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")
                break
        
        raise ValueError("Could not read CSV file with any supported encoding")
    
    def _read_excel(self, uploaded_file) -> pd.DataFrame:
        """
        Read Excel file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            pd.DataFrame: Loaded dataframe
        """
        try:
            # Reset file pointer
            uploaded_file.seek(0)
            # Read Excel file
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            st.success("Excel file loaded successfully")
            return df
        except Exception as e:
            st.error(f"Error reading Excel file: {str(e)}")
            # Try with different engine if openpyxl fails
            try:
                uploaded_file.seek(0)
                df = pd.read_excel(uploaded_file, engine='xlrd')
                st.success("Excel file loaded successfully with xlrd engine")
                return df
            except Exception as e2:
                st.error(f"Error reading Excel file with both engines: {str(e2)}")
                raise
    
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
        
        return max(delimiter_counts, key=delimiter_counts.get)
    
    def preview_data(self, df: pd.DataFrame, num_rows: int = 5) -> None:
        """
        Display a preview of the loaded data.
        
        Args:
            df: Dataframe to preview
            num_rows: Number of rows to show
        """
        st.subheader("Data Preview")
        from .helpers import prepare_df_for_display
        st.dataframe(prepare_df_for_display(df.head(num_rows)), use_container_width=True)
        
        # Show basic statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", len(df))
        with col2:
            st.metric("Total Columns", len(df.columns))
        with col3:
            st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
