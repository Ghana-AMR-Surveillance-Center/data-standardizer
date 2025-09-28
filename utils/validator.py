"""
Validator Module
Handles data validation and quality checks.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

class DataValidator:
    """Handles data validation operations."""
    
    def __init__(self):
        # Define validation rules for each expected column
        self.validation_rules = {
            'Patient_ID': {
                'required': True,
                'unique': True,
                'format': r'^[A-Z0-9-]+$',
                'min_length': 5
            },
            'Age': {
                'required': True,
                'type': 'numeric',
                'min_value': 0,
                'max_value': 120
            },
            'Gender': {
                'required': True,
                'allowed_values': ['M', 'F', 'O', 'U']
            },
            'Date_of_Admission': {
                'required': True,
                'type': 'date',
                'not_future': True
            },
            'Specimen_Type': {
                'required': True,
                'not_empty': True
            },
            'Organism': {
                'required': True,
                'not_empty': True
            }
        }
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate dataframe against defined rules.
        
        Args:
            df: Input dataframe
            
        Returns:
            Dict containing validation results
        """
        results = {
            'summary': {'total_errors': 0, 'total_warnings': 0},
            'errors': [],
            'warnings': [],
            'column_stats': {}
        }
        
        # Validate each column
        for column, rules in self.validation_rules.items():
            if column not in df.columns:
                if rules.get('required', False):
                    results['errors'].append({
                        'type': 'missing_column',
                        'column': column,
                        'message': f"Required column '{column}' is missing"
                    })
                continue
            
            column_results = self._validate_column(df[column], rules)
            results['summary']['total_errors'] += len(column_results['errors'])
            results['summary']['total_warnings'] += len(column_results['warnings'])
            results['errors'].extend(column_results['errors'])
            results['warnings'].extend(column_results['warnings'])
            results['column_stats'][column] = column_results['stats']
        
        return results
    
    def _validate_column(self, series: pd.Series, rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single column against its rules.
        
        Args:
            series: Column data
            rules: Validation rules
            
        Returns:
            Dict containing validation results for the column
        """
        results = {
            'errors': [],
            'warnings': [],
            'stats': {
                'total_rows': len(series),
                'null_count': series.isna().sum(),
                'unique_count': series.nunique()
            }
        }
        
        column_name = series.name
        
        # Check required
        if rules.get('required', False):
            null_mask = series.isna()
            null_count = null_mask.sum()
            if null_count > 0:
                results['errors'].append({
                    'type': 'missing_values',
                    'column': column_name,
                    'rows': null_mask[null_mask].index.tolist(),
                    'message': f"Found {null_count} missing values in required column '{column_name}'"
                })
        
        # Check uniqueness
        if rules.get('unique', False):
            duplicates = series.duplicated()
            duplicate_count = duplicates.sum()
            if duplicate_count > 0:
                results['errors'].append({
                    'type': 'duplicate_values',
                    'column': column_name,
                    'rows': duplicates[duplicates].index.tolist(),
                    'message': f"Found {duplicate_count} duplicate values in column '{column_name}'"
                })
        
        # Check format
        if 'format' in rules:
            try:
                invalid_format = ~series.astype(str).str.match(rules['format'])
                invalid_count = invalid_format.sum()
                if invalid_count > 0:
                    results['errors'].append({
                        'type': 'invalid_format',
                        'column': column_name,
                        'rows': invalid_format[invalid_format].index.tolist(),
                        'message': f"Found {invalid_count} values with invalid format in column '{column_name}'"
                    })
            except Exception as e:
                results['warnings'].append({
                    'type': 'format_check_failed',
                    'column': column_name,
                    'message': f"Could not validate format for column '{column_name}': {str(e)}"
                })
        
        # Check allowed values
        if 'allowed_values' in rules:
            invalid_values = ~series.isin(rules['allowed_values'])
            invalid_count = invalid_values.sum()
            if invalid_count > 0:
                results['errors'].append({
                    'type': 'invalid_values',
                    'column': column_name,
                    'rows': invalid_values[invalid_values].index.tolist(),
                    'message': f"Found {invalid_count} invalid values in column '{column_name}'"
                })
        
        # Check numeric constraints
        if rules.get('type') == 'numeric':
            non_numeric = ~pd.to_numeric(series, errors='coerce').notna()
            non_numeric_count = non_numeric.sum()
            if non_numeric_count > 0:
                results['errors'].append({
                    'type': 'non_numeric',
                    'column': column_name,
                    'rows': non_numeric[non_numeric].index.tolist(),
                    'message': f"Found {non_numeric_count} non-numeric values in column '{column_name}'"
                })
            
            if 'min_value' in rules:
                below_min = series < rules['min_value']
                below_min_count = below_min.sum()
                if below_min_count > 0:
                    results['errors'].append({
                        'type': 'below_minimum',
                        'column': column_name,
                        'rows': below_min[below_min].index.tolist(),
                        'message': f"Found {below_min_count} values below minimum in column '{column_name}'"
                    })
            
            if 'max_value' in rules:
                above_max = series > rules['max_value']
                above_max_count = above_max.sum()
                if above_max_count > 0:
                    results['errors'].append({
                        'type': 'above_maximum',
                        'column': column_name,
                        'rows': above_max[above_max].index.tolist(),
                        'message': f"Found {above_max_count} values above maximum in column '{column_name}'"
                    })
        
        # Check date constraints
        if rules.get('type') == 'date':
            # Convert to datetime
            dates = pd.to_datetime(series, errors='coerce')
            invalid_dates = dates.isna() & ~series.isna()
            invalid_count = invalid_dates.sum()
            if invalid_count > 0:
                results['errors'].append({
                    'type': 'invalid_dates',
                    'column': column_name,
                    'rows': invalid_dates[invalid_dates].index.tolist(),
                    'message': f"Found {invalid_count} invalid dates in column '{column_name}'"
                })
            
            if rules.get('not_future', False):
                future_dates = dates > pd.Timestamp.now()
                future_count = future_dates.sum()
                if future_count > 0:
                    results['errors'].append({
                        'type': 'future_dates',
                        'column': column_name,
                        'rows': future_dates[future_dates].index.tolist(),
                        'message': f"Found {future_count} future dates in column '{column_name}'"
                    })
        
        return results
    
    def show_validation_results(self, results: Dict[str, Any]) -> None:
        """
        Display validation results in Streamlit.
        
        Args:
            results: Validation results dictionary
        """
        if not results:
            st.warning("No validation results available")
            return
        
        # Show summary
        st.write("### Validation Summary")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Errors", results['summary']['total_errors'])
        with col2:
            st.metric("Total Warnings", results['summary']['total_warnings'])
        
        # Show errors
        if results['errors']:
            st.write("### Errors")
            for error in results['errors']:
                error_message = []
                if 'message' in error:
                    error_message.append(error['message'])
                if 'type' in error:
                    error_message.append(f"Type: {error['type']}")
                if 'rows' in error:
                    error_message.append(f"Affected rows: {len(error['rows'])}")
                st.error("\n".join(error_message))
        
        # Show warnings
        if results['warnings']:
            st.write("### Warnings")
            for warning in results['warnings']:
                warning_message = []
                if 'message' in warning:
                    warning_message.append(warning['message'])
                if 'type' in warning:
                    warning_message.append(f"Type: {warning['type']}")
                if 'rows' in warning:
                    warning_message.append(f"Affected rows: {len(warning['rows'])}")
                st.warning("\n".join(warning_message))
        
        # Show column statistics
        st.write("### Column Statistics")
        stats_df = pd.DataFrame.from_dict(
            results['column_stats'],
            orient='index'
        )
        st.dataframe(stats_df, use_container_width=True)
