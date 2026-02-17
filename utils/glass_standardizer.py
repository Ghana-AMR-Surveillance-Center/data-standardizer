"""
AMR Data Harmonizer - GLASS Standardization Module
Comprehensive standardization for GLASS (Global Antimicrobial Resistance Surveillance System) data submission.

This module provides:
- GLASS-specific column requirements and validation
- Automatic data cleaning for common AMR data issues
- Standardization of organism names, specimen types, and antimicrobial results
- GLASS submission format compliance
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime

class GLASSStandardizer:
    """
    Comprehensive GLASS data standardization for non-technical users.
    Handles automatic cleaning, standardization, and validation for GLASS submission.
    """
    
    # GLASS Required Core Fields
    GLASS_REQUIRED_FIELDS = {
        'Organism': {
            'required': True,
            'description': 'Organism name (e.g., E. coli, S. aureus)',
            'standardize': True
        },
        'Specimen type': {
            'required': True,
            'description': 'Type of specimen (e.g., Blood, Urine, Sputum)',
            'standardize': True
        },
        'Specimen date': {
            'required': True,
            'description': 'Date when specimen was collected',
            'type': 'date'
        },
        'Age in years': {
            'required': True,
            'description': 'Patient age in years',
            'type': 'numeric',
            'range': (0, 120)
        },
        'Gender': {
            'required': True,
            'description': 'Patient gender (M, F, O, U)',
            'allowed_values': ['M', 'F', 'O', 'U', 'Male', 'Female', 'Other', 'Unknown']
        }
    }
    
    # GLASS Optional Fields
    GLASS_OPTIONAL_FIELDS = {
        'Country': {'description': 'Country name'},
        'Institution': {'description': 'Hospital or laboratory name'},
        'Unique ID': {'description': 'Unique patient/specimen identifier'},
        'Specimen number': {'description': 'Specimen identification number'},
        'Location type': {'description': 'Type of location (e.g., Inpatient, Outpatient)'},
        'Department': {'description': 'Hospital department'},
        'End of Year data': {'description': 'Year of data collection'}
    }
    
    # Common organism name mappings (standardize to GLASS format)
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
    
    # Specimen type standardizations
    SPECIMEN_TYPE_MAPPINGS = {
        'blood': 'Blood',
        'urine': 'Urine',
        'sputum': 'Sputum',
        'wound': 'Wound',
        'swab': 'Swab',
        'stool': 'Stool',
        'csf': 'CSF',
        'cerebrospinal fluid': 'CSF',
        'pus': 'Pus',
        'tissue': 'Tissue',
        'other': 'Other',
        'cecum': 'CECUM',
        'rectal': 'Rectal',
        'nasal': 'Nasal',
        'throat': 'Throat'
    }
    
    # Gender standardizations
    GENDER_MAPPINGS = {
        'male': 'M',
        'm': 'M',
        'man': 'M',
        'female': 'F',
        'f': 'F',
        'woman': 'F',
        'other': 'O',
        'o': 'O',
        'unknown': 'U',
        'u': 'U',
        'unspecified': 'U'
    }
    
    # Antimicrobial result standardizations (SIR format)
    ANTIMICROBIAL_RESULT_MAPPINGS = {
        's': 'S',
        'susceptible': 'S',
        'susceptibility': 'S',
        'r': 'R',
        'resistant': 'R',
        'resistance': 'R',
        'i': 'I',
        'intermediate': 'I',
        'nd': 'ND',
        'not determined': 'ND',
        'nm': 'NM',
        'not measured': 'NM',
        'na': 'ND',
        'not applicable': 'ND'
    }
    
    def __init__(self):
        """Initialize GLASS standardizer."""
        self.cleaning_report = {
            'issues_found': [],
            'issues_fixed': [],
            'warnings': [],
            'statistics': {}
        }
    
    def standardize_for_glass(self, df: pd.DataFrame, auto_fix: bool = True) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Comprehensive GLASS standardization pipeline.
        
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
        
        # Step 1: Clean column names
        standardized_df = self._standardize_column_names(standardized_df)
        
        # Step 2: Standardize organism names
        standardized_df = self._standardize_organisms(standardized_df)
        
        # Step 3: Standardize specimen types
        standardized_df = self._standardize_specimen_types(standardized_df)
        
        # Step 4: Standardize gender values
        standardized_df = self._standardize_gender(standardized_df)
        
        # Step 5: Standardize antimicrobial results
        standardized_df = self._standardize_antimicrobial_results(standardized_df)
        
        # Step 6: Clean and standardize dates
        standardized_df = self._standardize_dates(standardized_df)
        
        # Step 7: Standardize age values
        standardized_df = self._standardize_age(standardized_df)
        
        # Step 8: Remove invalid rows
        if auto_fix:
            standardized_df = self._remove_invalid_rows(standardized_df)
        
        # Step 9: Validate GLASS requirements
        validation_results = self._validate_glass_requirements(standardized_df)
        
        self.cleaning_report['statistics']['rows_after_cleaning'] = len(standardized_df)
        self.cleaning_report['statistics']['columns_after_cleaning'] = len(standardized_df.columns)
        self.cleaning_report['validation'] = validation_results
        
        return standardized_df, self.cleaning_report
    
    def _standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to GLASS format (case-insensitive, whitespace-insensitive)."""
        from .column_utils import normalize_column_name
        
        column_mapping = {}
        
        for col in df.columns:
            col_normalized = normalize_column_name(col)  # Case-insensitive, strip whitespace
            
            # Map common variations to GLASS standard names (case-insensitive matching)
            if any(term in col_normalized for term in ['organism', 'bacteria', 'isolate']):
                if 'Organism' not in column_mapping.values():
                    column_mapping[col] = 'Organism'
            
            elif 'specimen' in col_normalized and 'type' in col_normalized:
                if 'Specimen type' not in column_mapping.values():
                    column_mapping[col] = 'Specimen type'
            
            elif 'specimen' in col_normalized and any(term in col_normalized for term in ['date', 'collection']):
                if 'Specimen date' not in column_mapping.values():
                    column_mapping[col] = 'Specimen date'
            
            elif 'age' in col_normalized:
                if 'Age in years' not in column_mapping.values():
                    column_mapping[col] = 'Age in years'
            
            elif 'gender' in col_normalized or 'sex' in col_normalized:
                if 'Gender' not in column_mapping.values():
                    column_mapping[col] = 'Gender'
        
        if column_mapping:
            df = df.rename(columns=column_mapping)
            self.cleaning_report['issues_fixed'].append(f"Standardized {len(column_mapping)} column names")
        
        return df
    
    def _standardize_organisms(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize organism names to GLASS format."""
        from .column_utils import find_column_case_insensitive
        
        organism_col = find_column_case_insensitive(df, 'Organism')
        if organism_col is None:
            return df
        
        original_count = df[organism_col].nunique()
        
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
        
        df[organism_col] = df[organism_col].apply(standardize_organism)
        
        # Rename to standard name if different
        if organism_col != 'Organism':
            df = df.rename(columns={organism_col: 'Organism'})
        
        new_count = df['Organism'].nunique()
        if original_count != new_count:
            self.cleaning_report['issues_fixed'].append(
                f"Standardized organism names: {original_count} → {new_count} unique values"
            )
        
        return df
    
    def _standardize_specimen_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize specimen types to GLASS format."""
        from .column_utils import find_column_case_insensitive
        
        spec_type_col = find_column_case_insensitive(df, 'Specimen type')
        if spec_type_col is None:
            return df
        
        def standardize_specimen(specimen):
            if pd.isna(specimen):
                return specimen
            
            spec_str = str(specimen).strip().lower()
            
            # Check direct mappings
            if spec_str in self.SPECIMEN_TYPE_MAPPINGS:
                return self.SPECIMEN_TYPE_MAPPINGS[spec_str]
            
            # Check partial matches
            for key, value in self.SPECIMEN_TYPE_MAPPINGS.items():
                if key in spec_str:
                    return value
            
            # Return title case if no mapping found
            return str(specimen).strip().title()
        
        df[spec_type_col] = df[spec_type_col].apply(standardize_specimen)
        
        # Rename to standard name if different
        if spec_type_col != 'Specimen type':
            df = df.rename(columns={spec_type_col: 'Specimen type'})
        
        self.cleaning_report['issues_fixed'].append("Standardized specimen type values")
        
        return df
    
    def _standardize_gender(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize gender values to GLASS format (M, F, O, U)."""
        from .column_utils import find_column_case_insensitive
        
        gender_col = find_column_case_insensitive(df, 'Gender')
        if gender_col is None:
            return df
        
        def standardize_gender(gender):
            if pd.isna(gender):
                return gender
            
            gender_str = str(gender).strip().lower()
            
            if gender_str in self.GENDER_MAPPINGS:
                return self.GENDER_MAPPINGS[gender_str]
            
            return str(gender).strip().upper()[:1]  # Take first character and uppercase
        
        df[gender_col] = df[gender_col].apply(standardize_gender)
        
        # Rename to standard name if different
        if gender_col != 'Gender':
            df = df.rename(columns={gender_col: 'Gender'})
        
        self.cleaning_report['issues_fixed'].append("Standardized gender values to M/F/O/U format")
        
        return df
    
    def _standardize_antimicrobial_results(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize antimicrobial susceptibility results to S/R/I/ND/NM format."""
        # Find antimicrobial columns (columns ending with SIR or containing antimicrobial names)
        antimicrobial_columns = []
        
        from .column_utils import normalize_column_name
        
        for col in df.columns:
            col_normalized = normalize_column_name(col)  # Case-insensitive, strip whitespace
            if 'sir' in col_normalized or any(ab in col_normalized for ab in [
                'ampicillin', 'amoxicillin', 'cefuroxime', 'cefotaxime', 'ceftriaxone',
                'gentamicin', 'ciprofloxacin', 'meropenem', 'imipenem', 'vancomycin'
            ]):
                antimicrobial_columns.append(col)
        
        for col in antimicrobial_columns:
            def standardize_result(value):
                if pd.isna(value):
                    return value
                
                value_str = str(value).strip().upper()
                
                # Check direct mappings
                if value_str in self.ANTIMICROBIAL_RESULT_MAPPINGS:
                    return self.ANTIMICROBIAL_RESULT_MAPPINGS[value_str]
                
                # Check partial matches
                for key, mapped_value in self.ANTIMICROBIAL_RESULT_MAPPINGS.items():
                    if key.upper() in value_str:
                        return mapped_value
                
                # If it's a single character, return uppercase
                if len(value_str) == 1 and value_str in ['S', 'R', 'I']:
                    return value_str
                
                return value_str
            
            df[col] = df[col].apply(standardize_result)
        
        if antimicrobial_columns:
            self.cleaning_report['issues_fixed'].append(
                f"Standardized {len(antimicrobial_columns)} antimicrobial result columns"
            )
        
        return df
    
    def _standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize date columns to consistent format."""
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        
        for col in date_columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
                self.cleaning_report['issues_fixed'].append(f"Standardized date format for {col}")
            except Exception:
                self.cleaning_report['warnings'].append(f"Could not standardize dates in {col}")
        
        return df
    
    def _standardize_age(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize age values to numeric years."""
        if 'Age in years' not in df.columns:
            return df
        
        def extract_age(age_value):
            if pd.isna(age_value):
                return age_value
            
            try:
                # Try direct numeric conversion
                age_num = float(age_value)
                if 0 <= age_num <= 120:
                    return age_num
            except (ValueError, TypeError):
                pass
            
            # Try to extract number from string
            age_str = str(age_value)
            numbers = re.findall(r'\d+', age_str)
            if numbers:
                age_num = float(numbers[0])
                if 0 <= age_num <= 120:
                    return age_num
            
            return None
        
        df['Age in years'] = df['Age in years'].apply(extract_age)
        self.cleaning_report['issues_fixed'].append("Standardized age values to numeric years")
        
        return df
    
    def _remove_invalid_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove rows that are clearly invalid (e.g., no organism, test data)."""
        original_len = len(df)
        
        # Remove rows with invalid organism names
        if 'Organism' in df.columns:
            invalid_organisms = ['xxx', 'test', 'no growth', 'contamination', 'not applicable', 'na', 'n/a']
            df = df[~df['Organism'].astype(str).str.lower().isin([x.lower() for x in invalid_organisms])]
        
        # Remove rows where all antimicrobial results are missing
        antimicrobial_cols = [col for col in df.columns if 'SIR' in col or any(ab in col.lower() for ab in [
            'ampicillin', 'amoxicillin', 'cefuroxime', 'cefotaxime', 'ceftriaxone'
        ])]
        
        if antimicrobial_cols:
            # Keep rows that have at least one antimicrobial result
            df = df[df[antimicrobial_cols].notna().any(axis=1)]
        
        removed = original_len - len(df)
        if removed > 0:
            self.cleaning_report['issues_fixed'].append(f"Removed {removed} invalid rows")
        
        return df
    
    def _validate_glass_requirements(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate data against GLASS requirements."""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'missing_required_fields': [],
            'completeness_scores': {}
        }
        
        # Check required fields
        for field, requirements in self.GLASS_REQUIRED_FIELDS.items():
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
        if 'Organism' in df.columns:
            unique_organisms = df['Organism'].nunique()
            if unique_organisms == 0:
                validation['errors'].append("No valid organisms found")
                validation['valid'] = False
            elif unique_organisms < 3:
                validation['warnings'].append(f"Very few organisms found: {unique_organisms}")
        
        # Check for antimicrobial data
        antimicrobial_cols = [col for col in df.columns if 'SIR' in col]
        if len(antimicrobial_cols) == 0:
            validation['warnings'].append("No antimicrobial susceptibility data found")
        
        return validation
    
    def show_cleaning_report(self, report: Dict[str, Any]):
        """Display cleaning report in Streamlit."""
        st.write("### 🧹 Data Cleaning Report")
        
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
                st.success("✅ **GLASS Validation: PASSED**")
            else:
                st.error("❌ **GLASS Validation: FAILED**")
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

