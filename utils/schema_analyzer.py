"""
Schema Analyzer Module
Analyzes and infers schema information from data files.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np

class SchemaAnalyzer:
    """Analyzes data schema and provides detailed information about columns."""
    
    STANDARD_FIELDS = [
        'End of Year data',
        'Country',
        'Unique ID',
        'Specimen number',
        'Institution',
        'Age in years',
        'Gender',
        'Specimen type',
        'Specimen date',
        'Location type',
        'Department',
        'Organism',
        'AmpicillinSIR',
        'Amoxicillin-ClavSIR',
        'CefuroximeSIR',
        'CefotximeSIR',
        'AmikacinSIR',
        'CeftriaxoneSIR',
        'CefoxitinSIR',  # Only one instance of CefoxitinSIR
        'CeftazidimeSIR',
        'AmoxicillinSIR',
        'TigecyclineSIR',
        'MeropenemSIR',
        'GentamicinSIR',
        'TetracyclineSIR',
        'CiprofloxacinSIR',
        'LEV-5',
        'PRL',
        'Co-trimoxasoleSIR',
        'FEP-30',
        'PenicillinSIR',
        'ErythromycinSIR',
        'ChloramphenicolSIR',
        'ClindamycinSIR',
        'AzithromycinSIR',
        'Neomycin',
        'Tobramycin',
        'TZP'
    ]
    
    def __init__(self):
        self.type_mappings = {
            'object': 'text',
            'int64': 'integer',
            'float64': 'decimal',
            'datetime64[ns]': 'date',
            'bool': 'boolean'
        }
        
    def analyze_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze the schema of a dataframe.
        
        Args:
            df: Input dataframe
            
        Returns:
            Dict containing schema information
        """
        return {
            'columns': self._analyze_columns(df),
            'row_count': len(df),
            'column_count': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum() / 1024**2  # MB
        }
        
    def _analyze_columns(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Analyze each column in the dataframe.
        
        Args:
            df: Input dataframe
            
        Returns:
            Dict containing column analysis
        """
        columns = {}
        
        for column in df.columns:
            columns[column] = {
                'type': self._get_column_type(df[column]),
                'unique_count': df[column].nunique(),
                'missing_count': df[column].isna().sum(),
                'sample_values': self._get_sample_values(df[column]),
                'stats': self._get_column_statistics(df[column])
            }
            
        return columns
        
    def _get_column_type(self, series: pd.Series) -> str:
        """
        Infer the data type of a column.
        
        Args:
            series: Column data
            
        Returns:
            str: Inferred data type
        """
        if pd.api.types.is_datetime64_any_dtype(series):
            return 'date'
        elif pd.api.types.is_numeric_dtype(series):
            return 'numeric'
        elif pd.api.types.is_bool_dtype(series):
            return 'boolean'
        else:
            return 'text'
            
    def _get_sample_values(self, series: pd.Series, n: int = 5) -> List[str]:
        """
        Get sample values from a column.
        
        Args:
            series: Column data
            n: Number of samples
            
        Returns:
            List of sample values. Returns empty list if series is empty or all NA.
        """
        non_na_series = series.dropna()
        if len(non_na_series) == 0:
            return []
            
        sample_size = min(n, len(non_na_series))
        if series.dtype == 'object':
            return non_na_series.sample(n=sample_size).tolist()
        return [str(x) for x in non_na_series.sample(n=sample_size).tolist()]
        
    def _get_column_statistics(self, series: pd.Series) -> Dict[str, Any]:
        """
        Calculate statistics for a column.
        
        Args:
            series: Column data
            
        Returns:
            Dict containing statistical information
        """
        stats: Dict[str, Any] = {
            'missing_percentage': (series.isna().sum() / len(series)) * 100
        }
        
        if pd.api.types.is_numeric_dtype(series):
            numeric_stats = {
                'mean': float(series.mean()) if not series.empty else None,
                'median': float(series.median()) if not series.empty else None,
                'std': float(series.std()) if not series.empty else None,
                'min': float(series.min()) if not series.empty else None,
                'max': float(series.max()) if not series.empty else None
            }
            stats.update(numeric_stats)
        elif series.dtype == 'object':
            value_counts = series.value_counts()
            if not value_counts.empty:
                text_stats = {
                    'most_common': value_counts.index[0],
                    'most_common_count': int(value_counts.iloc[0]),
                    'unique_ratio': (series.nunique() / len(series)) * 100
                }
                stats.update(text_stats)
                
        return stats
