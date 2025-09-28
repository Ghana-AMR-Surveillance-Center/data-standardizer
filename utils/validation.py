"""
Comprehensive data validation system
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime
import streamlit as st

class DataValidator:
    """Comprehensive data validation system."""
    
    def __init__(self):
        self.validation_rules = self._get_default_rules()
    
    def _get_default_rules(self) -> Dict[str, Dict]:
        """Get default validation rules."""
        return {
            'required_fields': {
                'patient_id': ['patient_id', 'patientid', 'id', 'patient_id_number'],
                'age': ['age', 'patient_age', 'years_old'],
                'gender': ['gender', 'sex', 'patient_gender'],
                'date': ['date', 'date_received', 'collection_date', 'test_date']
            },
            'data_types': {
                'numeric': ['age', 'count', 'value', 'number', 'amount'],
                'date': ['date', 'time', 'created', 'updated'],
                'categorical': ['gender', 'status', 'result', 'type', 'category']
            },
            'value_ranges': {
                'age': (0, 120),
                'gender': ['male', 'female', 'm', 'f', 'unknown'],
                'result': ['positive', 'negative', 'pending', 'inconclusive']
            },
            'format_patterns': {
                'patient_id': r'^[A-Za-z0-9\-_]+$',
                'date': r'^\d{4}-\d{2}-\d{2}$',
                'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            }
        }
    
    def validate_dataframe(self, df: pd.DataFrame, context: str = "") -> Dict[str, Any]:
        """Comprehensive DataFrame validation."""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': [],
            'statistics': {},
            'quality_score': 0.0
        }
        
        try:
            # Basic structure validation
            self._validate_structure(df, validation_result)
            
            # Data type validation
            self._validate_data_types(df, validation_result)
            
            # Value validation
            self._validate_values(df, validation_result)
            
            # Completeness validation
            self._validate_completeness(df, validation_result)
            
            # Consistency validation
            self._validate_consistency(df, validation_result)
            
            # Calculate quality score
            validation_result['quality_score'] = self._calculate_quality_score(validation_result)
            
            # Generate statistics
            validation_result['statistics'] = self._generate_statistics(df)
            
        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Validation failed: {str(e)}")
        
        return validation_result
    
    def _validate_structure(self, df: pd.DataFrame, result: Dict):
        """Validate DataFrame structure."""
        if df.empty:
            result['errors'].append("DataFrame is empty")
            result['valid'] = False
            return
        
        if len(df.columns) == 0:
            result['errors'].append("DataFrame has no columns")
            result['valid'] = False
            return
        
        if len(df) == 0:
            result['warnings'].append("DataFrame has no rows")
        
        # Check for duplicate columns
        duplicate_cols = df.columns[df.columns.duplicated()].tolist()
        if duplicate_cols:
            result['errors'].append(f"Duplicate columns found: {duplicate_cols}")
            result['valid'] = False
    
    def _validate_data_types(self, df: pd.DataFrame, result: Dict):
        """Validate data types."""
        for col in df.columns:
            col_lower = col.lower()
            
            # Check for mixed types in object columns
            if df[col].dtype == 'object':
                sample_values = df[col].dropna().head(100)
                if len(sample_values) > 0:
                    # Check for mixed numeric and string types
                    numeric_count = 0
                    string_count = 0
                    
                    for value in sample_values:
                        try:
                            float(str(value))
                            numeric_count += 1
                        except (ValueError, TypeError):
                            string_count += 1
                    
                    if numeric_count > 0 and string_count > 0:
                        result['warnings'].append(f"Column '{col}' contains mixed data types")
                        result['suggestions'].append(f"Consider standardizing data types in column '{col}'")
            
            # Check for appropriate data types based on column name
            if any(keyword in col_lower for keyword in ['age', 'count', 'number']):
                if not pd.api.types.is_numeric_dtype(df[col]):
                    result['warnings'].append(f"Column '{col}' appears to be numeric but has non-numeric data type")
                    result['suggestions'].append(f"Consider converting column '{col}' to numeric type")
    
    def _validate_values(self, df: pd.DataFrame, result: Dict):
        """Validate data values."""
        for col in df.columns:
            col_lower = col.lower()
            
            # Age validation
            if 'age' in col_lower and pd.api.types.is_numeric_dtype(df[col]):
                invalid_ages = df[(df[col] < 0) | (df[col] > 120)][col]
                if len(invalid_ages) > 0:
                    result['warnings'].append(f"Column '{col}' contains {len(invalid_ages)} invalid age values")
            
            # Date validation
            if 'date' in col_lower:
                try:
                    pd.to_datetime(df[col], errors='coerce')
                except:
                    result['warnings'].append(f"Column '{col}' contains invalid date values")
            
            # Categorical value validation
            if col_lower in ['gender', 'sex']:
                unique_values = df[col].dropna().str.lower().unique()
                valid_genders = ['male', 'female', 'm', 'f', 'unknown', 'other']
                invalid_values = [v for v in unique_values if v not in valid_genders]
                if invalid_values:
                    result['warnings'].append(f"Column '{col}' contains unexpected values: {invalid_values[:5]}")
    
    def _validate_completeness(self, df: pd.DataFrame, result: Dict):
        """Validate data completeness."""
        total_cells = len(df) * len(df.columns)
        null_cells = df.isnull().sum().sum()
        completeness = (total_cells - null_cells) / total_cells * 100
        
        result['statistics']['completeness'] = completeness
        
        if completeness < 80:
            result['warnings'].append(f"Low data completeness: {completeness:.1f}%")
        elif completeness < 95:
            result['warnings'].append(f"Moderate data completeness: {completeness:.1f}%")
        
        # Check for completely empty columns
        empty_cols = df.columns[df.isnull().all()].tolist()
        if empty_cols:
            result['warnings'].append(f"Empty columns found: {empty_cols}")
            result['suggestions'].append("Consider removing empty columns")
        
        # Check for completely empty rows
        empty_rows = df.isnull().all(axis=1).sum()
        if empty_rows > 0:
            result['warnings'].append(f"Found {empty_rows} completely empty rows")
            result['suggestions'].append("Consider removing empty rows")
    
    def _validate_consistency(self, df: pd.DataFrame, result: Dict):
        """Validate data consistency."""
        # Check for duplicate rows
        duplicate_rows = df.duplicated().sum()
        if duplicate_rows > 0:
            result['warnings'].append(f"Found {duplicate_rows} duplicate rows")
            result['suggestions'].append("Consider removing duplicate rows")
        
        # Check for inconsistent formatting
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check for inconsistent case
                unique_values = df[col].dropna().unique()
                if len(unique_values) > 1:
                    case_variations = {}
                    for value in unique_values:
                        lower_value = str(value).lower()
                        if lower_value not in case_variations:
                            case_variations[lower_value] = []
                        case_variations[lower_value].append(value)
                    
                    inconsistent_cases = [variations for variations in case_variations.values() if len(variations) > 1]
                    if inconsistent_cases:
                        result['warnings'].append(f"Column '{col}' has inconsistent case formatting")
                        result['suggestions'].append(f"Consider standardizing case in column '{col}'")
    
    def _calculate_quality_score(self, result: Dict) -> float:
        """Calculate overall data quality score."""
        score = 100.0
        
        # Deduct points for errors
        score -= len(result['errors']) * 20
        
        # Deduct points for warnings
        score -= len(result['warnings']) * 5
        
        # Deduct points for low completeness
        completeness = result['statistics'].get('completeness', 100)
        if completeness < 95:
            score -= (95 - completeness) * 0.5
        
        return max(0, min(100, score))
    
    def _generate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive statistics."""
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'completeness': (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
            'duplicate_rows': df.duplicated().sum(),
            'empty_rows': df.isnull().all(axis=1).sum(),
            'empty_columns': df.isnull().all().sum(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'data_types': df.dtypes.value_counts().to_dict()
        }
    
    def show_validation_report(self, validation_result: Dict[str, Any]):
        """Display validation report in Streamlit."""
        st.markdown("### 🔍 Data Validation Report")
        
        # Quality score
        quality_score = validation_result['quality_score']
        if quality_score >= 90:
            st.success(f"✅ Data Quality Score: {quality_score:.1f}/100")
        elif quality_score >= 70:
            st.warning(f"⚠️ Data Quality Score: {quality_score:.1f}/100")
        else:
            st.error(f"❌ Data Quality Score: {quality_score:.1f}/100")
        
        # Statistics
        stats = validation_result['statistics']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Rows", f"{stats['rows']:,}")
        with col2:
            st.metric("Columns", stats['columns'])
        with col3:
            st.metric("Completeness", f"{stats['completeness']:.1f}%")
        with col4:
            st.metric("Memory Usage", f"{stats['memory_usage_mb']:.1f}MB")
        
        # Errors
        if validation_result['errors']:
            st.error("### ❌ Errors")
            for error in validation_result['errors']:
                st.error(f"• {error}")
        
        # Warnings
        if validation_result['warnings']:
            st.warning("### ⚠️ Warnings")
            for warning in validation_result['warnings']:
                st.warning(f"• {warning}")
        
        # Suggestions
        if validation_result['suggestions']:
            st.info("### 💡 Suggestions")
            for suggestion in validation_result['suggestions']:
                st.info(f"• {suggestion}")

# Global validator instance
data_validator = DataValidator()
