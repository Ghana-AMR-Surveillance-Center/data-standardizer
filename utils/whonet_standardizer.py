"""
WHONET Data Standardizer Module
Comprehensive standardization for WHONET (World Health Organization Network) data format.

WHONET is a software for the management and analysis of microbiology laboratory data.
This module provides automatic cleaning and standardization for WHONET import.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime

class WHONETStandardizer:
    """
    Comprehensive WHONET data standardization for non-technical users.
    Handles automatic cleaning, standardization, and validation for WHONET import.
    """
    
    # WHONET Required Fields (based on WHONET data format)
    WHONET_REQUIRED_FIELDS = {
        'ORGANISM': {
            'required': True,
            'description': 'Organism name (e.g., E. coli, S. aureus)',
            'standardize': True,
            'max_length': 50
        },
        'SPEC_DATE': {
            'required': True,
            'description': 'Specimen collection date',
            'type': 'date',
            'format': 'YYYY-MM-DD'
        },
        'AGE': {
            'required': False,
            'description': 'Patient age',
            'type': 'numeric',
            'range': (0, 120)
        },
        'SEX': {
            'required': False,
            'description': 'Patient sex (M, F, U)',
            'allowed_values': ['M', 'F', 'U']
        }
    }
    
    # WHONET Antimicrobial Result Format
    WHONET_SIR_VALUES = ['S', 'R', 'I', 'ND', 'NM', 'MS', 'MR']
    
    # Organism name mappings (standardize to WHONET format)
    ORGANISM_MAPPINGS = {
        # E. coli variations
        'e coli': 'E. coli',
        'e.coli': 'E. coli',
        'escherichia coli': 'E. coli',
        'ecoli': 'E. coli',
        
        # S. aureus variations
        's aureus': 'S. aureus',
        's.aureus': 'S. aureus',
        'staphylococcus aureus': 'S. aureus',
        'staph aureus': 'S. aureus',
        'saureus': 'S. aureus',
        
        # K. pneumoniae variations
        'k pneumoniae': 'K. pneumoniae',
        'k.pneumoniae': 'K. pneumoniae',
        'klebsiella pneumoniae': 'K. pneumoniae',
        'kpneumoniae': 'K. pneumoniae',
        
        # P. aeruginosa variations
        'p aeruginosa': 'P. aeruginosa',
        'p.aeruginosa': 'P. aeruginosa',
        'pseudomonas aeruginosa': 'P. aeruginosa',
        'paeruginosa': 'P. aeruginosa',
        
        # A. baumannii variations
        'a baumannii': 'A. baumannii',
        'a.baumannii': 'A. baumannii',
        'acinetobacter baumannii': 'A. baumannii',
        'abaumannii': 'A. baumannii',
        
        # S. pneumoniae variations
        's pneumoniae': 'S. pneumoniae',
        's.pneumoniae': 'S. pneumoniae',
        'streptococcus pneumoniae': 'S. pneumoniae',
        'spneumoniae': 'S. pneumoniae',
    }
    
    # Specimen type mappings for WHONET
    SPECIMEN_TYPE_MAPPINGS = {
        'blood': 'BLOOD',
        'urine': 'URINE',
        'sputum': 'SPUTUM',
        'wound': 'WOUND',
        'swab': 'SWAB',
        'stool': 'STOOL',
        'csf': 'CSF',
        'cerebrospinal fluid': 'CSF',
        'pus': 'PUS',
        'tissue': 'TISSUE',
        'other': 'OTHER'
    }
    
    # Sex/Gender mappings for WHONET
    SEX_MAPPINGS = {
        'male': 'M',
        'm': 'M',
        'man': 'M',
        'female': 'F',
        'f': 'F',
        'woman': 'F',
        'unknown': 'U',
        'u': 'U',
        'unspecified': 'U',
        'other': 'U'
    }
    
    def __init__(self):
        """Initialize WHONET standardizer."""
        self.cleaning_report = {
            'issues_found': [],
            'issues_fixed': [],
            'warnings': [],
            'statistics': {}
        }
    
    def standardize_for_whonet(self, df: pd.DataFrame, auto_fix: bool = True) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Comprehensive WHONET standardization pipeline.
        
        Args:
            df: Input dataframe
            auto_fix: Whether to automatically fix common issues
            
        Returns:
            Tuple of (standardized dataframe, cleaning report)
        """
        self.cleaning_report = {
            'issues_found': [],
            'issues_fixed': [],
            'warnings': [],
            'statistics': {
                'original_rows': len(df),
                'original_columns': len(df.columns),
                'rows_after_cleaning': 0,
                'columns_after_cleaning': 0
            }
        }
        
        standardized_df = df.copy()
        
        # Step 1: Standardize column names to WHONET format
        standardized_df = self._standardize_column_names(standardized_df)
        
        # Step 2: Standardize organism names
        standardized_df = self._standardize_organisms(standardized_df)
        
        # Step 3: Standardize specimen types
        standardized_df = self._standardize_specimen_types(standardized_df)
        
        # Step 4: Standardize sex/gender values
        standardized_df = self._standardize_sex(standardized_df)
        
        # Step 5: Standardize antimicrobial results (SIR format)
        standardized_df = self._standardize_antimicrobial_results(standardized_df)
        
        # Step 6: Standardize dates to WHONET format
        standardized_df = self._standardize_dates(standardized_df)
        
        # Step 7: Standardize age values
        standardized_df = self._standardize_age(standardized_df)
        
        # Step 8: Remove invalid rows
        if auto_fix:
            standardized_df = self._remove_invalid_rows(standardized_df)
        
        # Step 9: Validate WHONET requirements
        validation_results = self._validate_whonet_requirements(standardized_df)
        
        self.cleaning_report['statistics']['rows_after_cleaning'] = len(standardized_df)
        self.cleaning_report['statistics']['columns_after_cleaning'] = len(standardized_df.columns)
        self.cleaning_report['validation'] = validation_results
        
        return standardized_df, self.cleaning_report
    
    def _standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to WHONET format (case-insensitive, whitespace-insensitive)."""
        from .column_utils import normalize_column_name
        
        column_mapping = {}
        
        for col in df.columns:
            col_normalized = normalize_column_name(col)  # Case-insensitive, strip whitespace
            
            # Map to WHONET standard column names (case-insensitive matching)
            if any(term in col_normalized for term in ['organism', 'bacteria', 'isolate']):
                if 'ORGANISM' not in column_mapping.values():
                    column_mapping[col] = 'ORGANISM'
            
            elif 'specimen' in col_normalized and any(term in col_normalized for term in ['date', 'collection']):
                if 'SPEC_DATE' not in column_mapping.values():
                    column_mapping[col] = 'SPEC_DATE'
            
            elif 'specimen' in col_normalized and 'type' in col_normalized:
                if 'SPEC_TYPE' not in column_mapping.values():
                    column_mapping[col] = 'SPEC_TYPE'
            
            elif 'age' in col_normalized:
                if 'AGE' not in column_mapping.values():
                    column_mapping[col] = 'AGE'
            
            elif 'sex' in col_normalized or 'gender' in col_normalized:
                if 'SEX' not in column_mapping.values():
                    column_mapping[col] = 'SEX'
            
            elif 'patient' in col_normalized and any(term in col_normalized for term in ['id', 'number']):
                if 'PATIENT_ID' not in column_mapping.values():
                    column_mapping[col] = 'PATIENT_ID'
        
        if column_mapping:
            df = df.rename(columns=column_mapping)
            self.cleaning_report['issues_fixed'].append(f"Standardized {len(column_mapping)} column names to WHONET format")
        
        # Convert all column names to uppercase (WHONET standard)
        df.columns = [col.upper() for col in df.columns]
        
        return df
    
    def _standardize_organisms(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize organism names to WHONET format."""
        if 'ORGANISM' not in df.columns:
            return df
        
        original_count = df['ORGANISM'].nunique()
        
        def standardize_organism(name):
            if pd.isna(name):
                return name
            
            name_str = str(name).strip().lower()
            
            # Check direct mappings
            if name_str in self.ORGANISM_MAPPINGS:
                return self.ORGANISM_MAPPINGS[name_str]
            
            # Check partial matches
            for key, value in self.ORGANISM_MAPPINGS.items():
                if key in name_str:
                    return value
            
            # Return title case if no mapping found
            return str(name).strip().title()
        
        df['ORGANISM'] = df['ORGANISM'].apply(standardize_organism)
        
        new_count = df['ORGANISM'].nunique()
        if original_count != new_count:
            self.cleaning_report['issues_fixed'].append(
                f"Standardized organism names: {original_count} → {new_count} unique values"
            )
        
        return df
    
    def _standardize_specimen_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize specimen types to WHONET format."""
        if 'SPEC_TYPE' not in df.columns:
            return df
        
        def standardize_specimen(specimen):
            if pd.isna(specimen):
                return specimen
            
            spec_str = str(specimen).strip().upper()
            
            # Check direct mappings
            if spec_str.lower() in self.SPECIMEN_TYPE_MAPPINGS:
                return self.SPECIMEN_TYPE_MAPPINGS[spec_str.lower()]
            
            # Check partial matches
            for key, value in self.SPECIMEN_TYPE_MAPPINGS.items():
                if key in spec_str.lower():
                    return value
            
            # Return uppercase if no mapping found
            return spec_str
        
        df['SPEC_TYPE'] = df['SPEC_TYPE'].apply(standardize_specimen)
        self.cleaning_report['issues_fixed'].append("Standardized specimen type values to WHONET format")
        
        return df
    
    def _standardize_sex(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize sex values to WHONET format (M, F, U)."""
        if 'SEX' not in df.columns:
            return df
        
        def standardize_sex(sex):
            if pd.isna(sex):
                return 'U'  # Unknown default for WHONET
            
            sex_str = str(sex).strip().lower()
            
            if sex_str in self.SEX_MAPPINGS:
                return self.SEX_MAPPINGS[sex_str]
            
            return 'U'  # Default to Unknown
        
        df['SEX'] = df['SEX'].apply(standardize_sex)
        self.cleaning_report['issues_fixed'].append("Standardized sex values to WHONET format (M/F/U)")
        
        return df
    
    def _standardize_antimicrobial_results(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize antimicrobial susceptibility results to WHONET SIR format."""
        # Find antimicrobial columns (columns that might contain SIR results)
        antimicrobial_columns = []
        
        for col in df.columns:
            col_upper = col.upper()
            # WHONET typically uses column names like "AMK_SIR", "AMP_SIR", etc.
            if '_SIR' in col_upper or 'SIR' in col_upper:
                antimicrobial_columns.append(col)
            # Also check for common antimicrobial abbreviations
            elif any(abbrev in col_upper for abbrev in [
                'AMP', 'AMK', 'AMX', 'AZM', 'CAZ', 'CIP', 'CLI', 'CRO', 'CTX',
                'ERY', 'GEN', 'IPM', 'MEM', 'PEN', 'TET', 'VAN'
            ]):
                antimicrobial_columns.append(col)
        
        for col in antimicrobial_columns:
            def standardize_result(value):
                if pd.isna(value):
                    return 'ND'  # Not Determined for WHONET
                
                value_str = str(value).strip().upper()
                
                # Direct match
                if value_str in self.WHONET_SIR_VALUES:
                    return value_str
                
                # Common variations
                if value_str in ['SUSCEPTIBLE', 'SENSITIVE', 'S']:
                    return 'S'
                elif value_str in ['RESISTANT', 'RESISTANCE', 'R']:
                    return 'R'
                elif value_str in ['INTERMEDIATE', 'I']:
                    return 'I'
                elif value_str in ['NOT DETERMINED', 'ND', 'N/A', 'NA']:
                    return 'ND'
                elif value_str in ['NOT MEASURED', 'NM']:
                    return 'NM'
                
                return 'ND'  # Default to Not Determined
            
            df[col] = df[col].apply(standardize_result)
        
        if antimicrobial_columns:
            self.cleaning_report['issues_fixed'].append(
                f"Standardized {len(antimicrobial_columns)} antimicrobial result columns to WHONET SIR format"
            )
        
        return df
    
    def _standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize date columns to WHONET format (YYYY-MM-DD)."""
        date_columns = [col for col in df.columns if 'DATE' in col.upper()]
        
        for col in date_columns:
            try:
                # Convert to datetime
                df[col] = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
                # Format as YYYY-MM-DD
                df[col] = df[col].dt.strftime('%Y-%m-%d')
                self.cleaning_report['issues_fixed'].append(f"Standardized date format for {col} to WHONET format (YYYY-MM-DD)")
            except Exception as e:
                self.cleaning_report['warnings'].append(f"Could not standardize dates in {col}: {str(e)}")
        
        return df
    
    def _standardize_age(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize age values to numeric."""
        if 'AGE' not in df.columns:
            return df
        
        def extract_age(age_value):
            if pd.isna(age_value):
                return None
            
            try:
                # Try direct numeric conversion
                age_num = float(age_value)
                if 0 <= age_num <= 120:
                    return int(age_num)
            except (ValueError, TypeError):
                pass
            
            # Try to extract number from string
            age_str = str(age_value)
            numbers = re.findall(r'\d+', age_str)
            if numbers:
                age_num = float(numbers[0])
                if 0 <= age_num <= 120:
                    return int(age_num)
            
            return None
        
        df['AGE'] = df['AGE'].apply(extract_age)
        self.cleaning_report['issues_fixed'].append("Standardized age values to numeric")
        
        return df
    
    def _remove_invalid_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove rows that are clearly invalid."""
        original_len = len(df)
        
        # Remove rows with invalid organism names
        if 'ORGANISM' in df.columns:
            invalid_organisms = ['XXX', 'TEST', 'NO GROWTH', 'CONTAMINATION', 'NOT APPLICABLE', 'NA', 'N/A']
            df = df[~df['ORGANISM'].astype(str).str.upper().isin(invalid_organisms)]
        
        # Remove rows where all antimicrobial results are missing
        antimicrobial_cols = [col for col in df.columns if '_SIR' in col or 'SIR' in col]
        
        if antimicrobial_cols:
            # Keep rows that have at least one antimicrobial result
            df = df[df[antimicrobial_cols].notna().any(axis=1)]
        
        removed = original_len - len(df)
        if removed > 0:
            self.cleaning_report['issues_fixed'].append(f"Removed {removed} invalid rows")
        
        return df
    
    def _validate_whonet_requirements(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate data against WHONET requirements."""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'missing_required_fields': [],
            'completeness_scores': {}
        }
        
        # Check required fields
        for field, requirements in self.WHONET_REQUIRED_FIELDS.items():
            if requirements.get('required', False):
                if field not in df.columns:
                    validation['missing_required_fields'].append(field)
                    validation['errors'].append(f"Missing required field: {field}")
                    validation['valid'] = False
                else:
                    # Calculate completeness
                    completeness = (df[field].notna().sum() / len(df)) * 100
                    validation['completeness_scores'][field] = completeness
                    
                    if completeness < 80:
                        validation['warnings'].append(
                            f"{field} has low completeness: {completeness:.1f}%"
                        )
        
        # Check for organism data
        if 'ORGANISM' in df.columns:
            unique_organisms = df['ORGANISM'].nunique()
            if unique_organisms == 0:
                validation['errors'].append("No valid organisms found")
                validation['valid'] = False
            elif unique_organisms < 3:
                validation['warnings'].append(f"Very few organisms found: {unique_organisms}")
        
        # Check for antimicrobial data
        antimicrobial_cols = [col for col in df.columns if '_SIR' in col or 'SIR' in col]
        if len(antimicrobial_cols) == 0:
            validation['warnings'].append("No antimicrobial susceptibility data found (no columns with '_SIR' suffix)")
        
        return validation
    
    def show_cleaning_report(self, report: Dict[str, Any]):
        """Display cleaning report in Streamlit."""
        st.write("### 🧹 WHONET Data Cleaning Report")
        
        stats = report.get('statistics', {})
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Original Rows", stats.get('original_rows', 0))
        with col2:
            st.metric("Rows After Cleaning", stats.get('rows_after_cleaning', 0))
        with col3:
            st.metric("Original Columns", stats.get('original_columns', 0))
        with col4:
            st.metric("Columns After Cleaning", stats.get('columns_after_cleaning', 0))
        
        # Issues fixed
        if report.get('issues_fixed'):
            st.success("✅ **Issues Fixed:**")
            for issue in report['issues_fixed']:
                st.write(f"- {issue}")
        
        # Warnings
        if report.get('warnings'):
            st.warning("⚠️ **Warnings:**")
            for warning in report['warnings']:
                st.write(f"- {warning}")
        
        # Validation results
        if 'validation' in report:
            validation = report['validation']
            
            if validation.get('valid'):
                st.success("✅ **WHONET Validation: PASSED**")
            else:
                st.error("❌ **WHONET Validation: FAILED**")
                st.write("**Errors:**")
                for error in validation.get('errors', []):
                    st.write(f"- {error}")
            
            if validation.get('warnings'):
                st.write("**Validation Warnings:**")
                for warning in validation['warnings']:
                    st.write(f"- {warning}")
            
            # Completeness scores
            if validation.get('completeness_scores'):
                st.write("**Data Completeness:**")
                for field, score in validation['completeness_scores'].items():
                    st.progress(score / 100, text=f"{field}: {score:.1f}%")

