"""
Data Profiling Module
Provides comprehensive data profiling and statistical analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class DataProfiler:
    """Provides comprehensive data profiling and analysis."""
    
    def __init__(self):
        self.profile_results = {}
    
    def profile_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Create comprehensive profile of a dataframe.
        
        Args:
            df: Input dataframe
            
        Returns:
            Dictionary containing profiling results
        """
        profile = {
            'overview': self._get_overview_stats(df),
            'columns': self._profile_columns(df),
            'data_types': self._analyze_data_types(df),
            'missing_data': self._analyze_missing_data(df),
            'duplicates': self._analyze_duplicates(df),
            'outliers': self._detect_outliers(df),
            'correlations': self._calculate_correlations(df),
            'patterns': self._detect_patterns(df)
        }
        
        self.profile_results = profile
        return profile
    
    def _get_overview_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get overview statistics."""
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'total_cells': df.size,
            'empty_cells': df.isna().sum().sum(),
            'duplicate_rows': df.duplicated().sum(),
            'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
            'text_columns': len(df.select_dtypes(include=['object']).columns),
            'datetime_columns': len(df.select_dtypes(include=['datetime']).columns)
        }
    
    def _profile_columns(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Profile individual columns."""
        column_profiles = {}
        
        for col in df.columns:
            series = df[col]
            profile = {
                'dtype': str(series.dtype),
                'non_null_count': series.notna().sum(),
                'null_count': series.isna().sum(),
                'null_percentage': (series.isna().sum() / len(series)) * 100,
                'unique_count': series.nunique(),
                'unique_percentage': (series.nunique() / len(series)) * 100,
                'most_common_value': series.mode().iloc[0] if not series.mode().empty else None,
                'most_common_count': series.value_counts().iloc[0] if not series.value_counts().empty else 0
            }
            
            # Add type-specific statistics
            if pd.api.types.is_numeric_dtype(series):
                profile.update({
                    'mean': series.mean(),
                    'median': series.median(),
                    'std': series.std(),
                    'min': series.min(),
                    'max': series.max(),
                    'skewness': series.skew(),
                    'kurtosis': series.kurtosis()
                })
            elif pd.api.types.is_datetime64_any_dtype(series):
                profile.update({
                    'min_date': series.min(),
                    'max_date': series.max(),
                    'date_range_days': (series.max() - series.min()).days if series.notna().any() else 0
                })
            else:
                # Text statistics
                profile.update({
                    'avg_length': series.astype(str).str.len().mean(),
                    'max_length': series.astype(str).str.len().max(),
                    'min_length': series.astype(str).str.len().min()
                })
            
            column_profiles[col] = profile
        
        return column_profiles
    
    def _analyze_data_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data type distribution."""
        type_counts = df.dtypes.value_counts().to_dict()
        type_percentages = {str(k): (v / len(df.columns)) * 100 for k, v in type_counts.items()}
        
        return {
            'type_counts': type_counts,
            'type_percentages': type_percentages,
            'mixed_type_columns': self._find_mixed_type_columns(df)
        }
    
    def _find_mixed_type_columns(self, df: pd.DataFrame) -> List[str]:
        """Find columns with mixed data types."""
        mixed_columns = []
        
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if column contains mixed types
                non_null_values = df[col].dropna()
                if len(non_null_values) > 0:
                    types = set(type(val).__name__ for val in non_null_values)
                    if len(types) > 1:
                        mixed_columns.append(col)
        
        return mixed_columns
    
    def _analyze_missing_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze missing data patterns."""
        missing_by_column = df.isna().sum().to_dict()
        missing_percentages = {col: (count / len(df)) * 100 for col, count in missing_by_column.items()}
        
        # Find columns with high missing data
        high_missing = {col: pct for col, pct in missing_percentages.items() if pct > 50}
        
        # Find rows with missing data
        rows_with_missing = df.isna().any(axis=1).sum()
        
        return {
            'missing_by_column': missing_by_column,
            'missing_percentages': missing_percentages,
            'high_missing_columns': high_missing,
            'rows_with_missing': rows_with_missing,
            'rows_with_missing_percentage': (rows_with_missing / len(df)) * 100
        }
    
    def _analyze_duplicates(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze duplicate data."""
        duplicate_rows = df.duplicated()
        duplicate_count = duplicate_rows.sum()
        
        # Find duplicate values in individual columns
        column_duplicates = {}
        for col in df.columns:
            col_duplicates = df[col].duplicated().sum()
            if col_duplicates > 0:
                column_duplicates[col] = col_duplicates
        
        return {
            'duplicate_rows': duplicate_count,
            'duplicate_rows_percentage': (duplicate_count / len(df)) * 100,
            'column_duplicates': column_duplicates
        }
    
    def _detect_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect outliers in numeric columns."""
        outliers = {}
        
        for col in df.select_dtypes(include=[np.number]).columns:
            series = df[col].dropna()
            if len(series) > 0:
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_mask = (series < lower_bound) | (series > upper_bound)
                outlier_count = outlier_mask.sum()
                
                if outlier_count > 0:
                    outliers[col] = {
                        'count': outlier_count,
                        'percentage': (outlier_count / len(series)) * 100,
                        'values': series[outlier_mask].tolist()
                    }
        
        return outliers
    
    def _calculate_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate correlations between numeric columns."""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return {'correlation_matrix': None, 'high_correlations': []}
        
        corr_matrix = numeric_df.corr()
        
        # Find high correlations
        high_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:  # High correlation threshold
                    high_correlations.append({
                        'column1': corr_matrix.columns[i],
                        'column2': corr_matrix.columns[j],
                        'correlation': corr_value
                    })
        
        return {
            'correlation_matrix': corr_matrix,
            'high_correlations': high_correlations
        }
    
    def _detect_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect patterns in the data."""
        patterns = {
            'constant_columns': [],
            'id_columns': [],
            'date_columns': [],
            'categorical_columns': []
        }
        
        for col in df.columns:
            # Check for constant columns
            if df[col].nunique() <= 1:
                patterns['constant_columns'].append(col)
            
            # Check for ID columns
            if any(keyword in col.lower() for keyword in ['id', 'key', 'index', 'number']):
                patterns['id_columns'].append(col)
            
            # Check for date columns
            if any(keyword in col.lower() for keyword in ['date', 'time', 'created', 'updated']):
                patterns['date_columns'].append(col)
            
            # Check for categorical columns
            if df[col].dtype == 'object' and df[col].nunique() < len(df) * 0.1:
                patterns['categorical_columns'].append(col)
        
        return patterns
    
    def show_profile_report(self, profile: Dict[str, Any]) -> None:
        """Display comprehensive profile report in Streamlit."""
        st.markdown("### 📊 Data Profile Report")
        
        # Overview
        overview = profile['overview']
        st.markdown("#### Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Rows", f"{overview['total_rows']:,}")
            st.metric("Total Columns", overview['total_columns'])
        
        with col2:
            st.metric("Memory Usage", f"{overview['memory_usage_mb']:.2f} MB")
            st.metric("Empty Cells", f"{overview['empty_cells']:,}")
        
        with col3:
            st.metric("Duplicate Rows", f"{overview['duplicate_rows']:,}")
            st.metric("Numeric Columns", overview['numeric_columns'])
        
        with col4:
            st.metric("Text Columns", overview['text_columns'])
            st.metric("Date Columns", overview['datetime_columns'])
        
        # Data types distribution
        st.markdown("#### Data Types Distribution")
        type_data = profile['data_types']
        if type_data['type_counts']:
            type_df = pd.DataFrame(list(type_data['type_counts'].items()), 
                                 columns=['Data Type', 'Count'])
            fig = px.pie(type_df, values='Count', names='Data Type', 
                        title="Column Data Types")
            st.plotly_chart(fig, use_container_width=True)
        
        # Missing data analysis
        st.markdown("#### Missing Data Analysis")
        missing_data = profile['missing_data']
        if missing_data['missing_by_column']:
            missing_df = pd.DataFrame(list(missing_data['missing_percentages'].items()),
                                    columns=['Column', 'Missing %'])
            missing_df = missing_df[missing_df['Missing %'] > 0].sort_values('Missing %', ascending=False)
            
            if not missing_df.empty:
                fig = px.bar(missing_df, x='Column', y='Missing %',
                           title="Missing Data by Column")
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
        
        # Outliers analysis
        outliers = profile['outliers']
        if outliers:
            st.markdown("#### Outliers Detection")
            for col, outlier_info in outliers.items():
                st.write(f"**{col}**: {outlier_info['count']} outliers ({outlier_info['percentage']:.1f}%)")
        
        # High correlations
        correlations = profile['correlations']
        if correlations['high_correlations']:
            st.markdown("#### High Correlations")
            corr_df = pd.DataFrame(correlations['high_correlations'])
            st.dataframe(corr_df, use_container_width=True)
        
        # Patterns
        patterns = profile['patterns']
        if any(patterns.values()):
            st.markdown("#### Detected Patterns")
            for pattern_type, columns in patterns.items():
                if columns:
                    st.write(f"**{pattern_type.replace('_', ' ').title()}**: {', '.join(columns)}")
