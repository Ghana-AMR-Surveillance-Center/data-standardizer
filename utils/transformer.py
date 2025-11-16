"""
Data Transformer Module
Handles data transformation operations with flexible AMR data cleaning capabilities.
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from datetime import datetime

class DataTransformer:
    """Handles data transformation operations with flexible AMR data cleaning."""
    
    def __init__(self):
        from .age_transformer import AgeTransformer
        self.age_transformer = AgeTransformer()
        self.transformations = {
            'text': {
                'uppercase': lambda x: x.astype(str).str.upper(),
                'lowercase': lambda x: x.astype(str).str.lower(),
                'titlecase': lambda x: x.astype(str).str.title(),
                'strip': lambda x: x.astype(str).str.strip(),
                'remove_special_chars': lambda x: x.astype(str).str.replace(r'[^a-zA-Z0-9\s]', '', regex=True),
                'extract_numbers': lambda x: pd.to_numeric(x.astype(str).str.extract(r'(\d+)', expand=False), errors='coerce')
            },
            'number': {
                'round': lambda x, decimals: x.round(decimals),
                'absolute': lambda x: x.abs(),
                'standardize': lambda x: (x - x.mean()) / x.std()
            },
            'date': {
                'to_iso_date': lambda x: pd.to_datetime(x).dt.date,
                'extract_year': lambda x: pd.to_datetime(x).dt.year,
                'extract_month': lambda x: pd.to_datetime(x).dt.month,
                'extract_day': lambda x: pd.to_datetime(x).dt.day
            }
        }
        
        # Initialize flexible cleaning strategies
        self.cleaning_strategies = self._initialize_cleaning_strategies()
    
    def _initialize_cleaning_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize flexible cleaning strategies for different AMR data formats."""
        return {
            'organism': {
                'patterns': [
                    (r'^e\.?\s*coli$', 'E. coli', re.IGNORECASE),
                    (r'^s\.?\s*aureus$', 'S. aureus', re.IGNORECASE),
                    (r'^k\.?\s*pneumoniae$', 'K. pneumoniae', re.IGNORECASE),
                    (r'^p\.?\s*aeruginosa$', 'P. aeruginosa', re.IGNORECASE),
                    (r'escherichia\s+coli', 'E. coli', re.IGNORECASE),
                    (r'staphylococcus\s+aureus', 'S. aureus', re.IGNORECASE),
                    (r'klebsiella\s+pneumoniae', 'K. pneumoniae', re.IGNORECASE),
                    (r'pseudomonas\s+aeruginosa', 'P. aeruginosa', re.IGNORECASE),
                ],
                'invalid_values': ['xxx', 'test', 'no growth', 'contamination', 'na', 'n/a', 'not applicable'],
                'normalize_case': True,
                'remove_extra_spaces': True
            },
            'antimicrobial_result': {
                'mappings': {
                    's': 'S', 'susceptible': 'S', 'susceptibility': 'S',
                    'r': 'R', 'resistant': 'R', 'resistance': 'R',
                    'i': 'I', 'intermediate': 'I', 'indeterminate': 'I',
                    'nd': 'ND', 'not determined': 'ND', 'not done': 'ND',
                    'nm': 'NM', 'not measured': 'NM', 'na': 'ND'
                },
                'normalize_case': True,
                'strip_whitespace': True
            },
            'specimen_type': {
                'mappings': {
                    'bld': 'Blood', 'bl': 'Blood', 'blood': 'Blood', 'whole blood': 'Blood',
                    'ur': 'Urine', 'urine': 'Urine', 'urine sample': 'Urine',
                    'sput': 'Sputum', 'sputum': 'Sputum', 'sputum sample': 'Sputum',
                    'csf': 'CSF', 'cerebrospinal fluid': 'CSF',
                    'wound': 'Wound', 'swab': 'Swab',
                    'stool': 'Stool', 'feces': 'Stool'
                },
                'normalize_case': True,
                'title_case_fallback': True
            },
            'gender': {
                'mappings': {
                    'male': 'M', 'm': 'M', 'man': 'M',
                    'female': 'F', 'f': 'F', 'woman': 'F',
                    'other': 'O', 'o': 'O',
                    'unknown': 'U', 'u': 'U', 'unspecified': 'U'
                },
                'normalize_case': True,
                'first_char_fallback': True
            },
            'date': {
                'formats': [
                    '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y',
                    '%d.%m.%Y', '%Y/%m/%d', '%d %m %Y', '%Y %m %d'
                ],
                'infer_datetime': True,
                'handle_timezone': True
            },
            'age': {
                'extract_patterns': [
                    r'(\d+)\s*years?',
                    r'(\d+)\s*yrs?',
                    r'(\d+)\s*yo',
                    r'age[:\s]*(\d+)',
                    r'(\d+)'
                ],
                'valid_range': (0, 120),
                'extract_from_text': True
            },
            'numeric': {
                'handle_scientific_notation': True,
                'handle_decimal_separators': ['.', ','],
                'remove_commas': True,
                'extract_from_text': True
            }
        }
    
    def flexible_clean_column(self, df: pd.DataFrame, column_name: str, 
                             strategy: str, custom_mappings: Optional[Dict] = None) -> pd.DataFrame:
        """
        Flexibly clean a column using predefined or custom strategies.
        
        Args:
            df: Input dataframe
            column_name: Name of column to clean
            strategy: Cleaning strategy ('organism', 'antimicrobial_result', 'specimen_type', 
                     'gender', 'date', 'age', 'numeric', 'custom')
            custom_mappings: Custom mappings for 'custom' strategy
            
        Returns:
            DataFrame with cleaned column
        """
        from .column_utils import find_column_case_insensitive
        
        actual_col = find_column_case_insensitive(df, column_name)
        if actual_col is None:
            return df
        
        df_cleaned = df.copy()
        
        # Get the actual column as Series to avoid type issues
        # Ensure we have a Series, not DataFrame
        if isinstance(df_cleaned[actual_col], pd.Series):
            col_series = df_cleaned[actual_col]
        else:
            # Fallback: convert to Series if needed
            col_series = pd.Series(df_cleaned[actual_col])
        
        if strategy == 'organism':
            df_cleaned[actual_col] = self._clean_organism_column(col_series)
        elif strategy == 'antimicrobial_result':
            df_cleaned[actual_col] = self._clean_antimicrobial_column(col_series)
        elif strategy == 'specimen_type':
            df_cleaned[actual_col] = self._clean_specimen_column(col_series)
        elif strategy == 'gender':
            df_cleaned[actual_col] = self._clean_gender_column(col_series)
        elif strategy == 'date':
            df_cleaned[actual_col] = self._clean_date_column(col_series)
        elif strategy == 'age':
            df_cleaned[actual_col] = self._clean_age_column(col_series)
        elif strategy == 'numeric':
            df_cleaned[actual_col] = self._clean_numeric_column(col_series)
        elif strategy == 'custom' and custom_mappings:
            df_cleaned[actual_col] = self._clean_with_custom_mappings(col_series, custom_mappings)
        else:
            # Default: strip whitespace and normalize case
            df_cleaned[actual_col] = df_cleaned[actual_col].astype(str).str.strip().str.title()
        
        return df_cleaned
    
    def _clean_organism_column(self, series: pd.Series) -> pd.Series:
        """Clean organism names using pattern matching and normalization."""
        strategy = self.cleaning_strategies['organism']
        
        def clean_organism(value):
            if pd.isna(value):
                return value
            
            value_str = str(value).strip()
            
            # Check for invalid values
            if value_str.lower() in [v.lower() for v in strategy['invalid_values']]:
                return None
            
            # Apply pattern matching
            for pattern, replacement, flags in strategy['patterns']:
                if re.match(pattern, value_str, flags):
                    return replacement
            
            # Normalize case and spacing
            if strategy['normalize_case']:
                value_str = value_str.title()
            if strategy['remove_extra_spaces']:
                value_str = re.sub(r'\s+', ' ', value_str).strip()
            
            return value_str
        
        return series.apply(clean_organism)
    
    def _clean_antimicrobial_column(self, series: pd.Series) -> pd.Series:
        """Clean antimicrobial results using mappings."""
        strategy = self.cleaning_strategies['antimicrobial_result']
        
        def clean_result(value):
            if pd.isna(value):
                return value
            
            value_str = str(value)
            if strategy['strip_whitespace']:
                value_str = value_str.strip()
            if strategy['normalize_case']:
                value_str = value_str.lower()
            
            return strategy['mappings'].get(value_str, value_str.upper() if len(value_str) == 1 else value_str)
        
        return series.apply(clean_result)
    
    def _clean_specimen_column(self, series: pd.Series) -> pd.Series:
        """Clean specimen types using mappings."""
        strategy = self.cleaning_strategies['specimen_type']
        
        def clean_specimen(value):
            if pd.isna(value):
                return value
            
            value_str = str(value)
            if strategy['normalize_case']:
                value_str = value_str.lower().strip()
            
            result = strategy['mappings'].get(value_str, None)
            if result:
                return result
            
            # Fallback to title case
            if strategy.get('title_case_fallback', False):
                return value_str.title()
            
            return value_str
        
        return series.apply(clean_specimen)
    
    def _clean_gender_column(self, series: pd.Series) -> pd.Series:
        """Clean gender values using mappings."""
        strategy = self.cleaning_strategies['gender']
        
        def clean_gender(value):
            if pd.isna(value):
                return 'U'
            
            value_str = str(value)
            if strategy['normalize_case']:
                value_str = value_str.lower().strip()
            
            result = strategy['mappings'].get(value_str, None)
            if result:
                return result
            
            # Fallback to first character
            if strategy.get('first_char_fallback', False) and len(value_str) > 0:
                return value_str[0].upper()
            
            return value_str.upper()[:1] if len(value_str) > 0 else 'U'
        
        return series.apply(clean_gender)
    
    def _clean_date_column(self, series: pd.Series) -> pd.Series:
        """Clean date columns with multiple format support."""
        strategy = self.cleaning_strategies['date']
        
        # Try pandas to_datetime with multiple formats
        if strategy['infer_datetime']:
            try:
                return pd.to_datetime(series, errors='coerce', infer_datetime_format=True)
            except:
                pass
        
        # Try specific formats
        for fmt in strategy['formats']:
            try:
                result = pd.to_datetime(series, format=fmt, errors='coerce')
                if result.notna().sum() > len(series) * 0.5:  # If >50% success, use this format
                    return result
            except:
                continue
        
        # Final fallback
        return pd.to_datetime(series, errors='coerce')
    
    def _clean_age_column(self, series: pd.Series) -> pd.Series:
        """Clean age values extracting numbers from various formats."""
        strategy = self.cleaning_strategies['age']
        
        def clean_age(value):
            if pd.isna(value):
                return None
            
            # Try direct numeric conversion
            try:
                age = float(value)
                if strategy['valid_range'][0] <= age <= strategy['valid_range'][1]:
                    return age
            except (ValueError, TypeError):
                pass
            
            # Try pattern extraction
            if strategy.get('extract_from_text', False):
                value_str = str(value).lower()
                for pattern in strategy['extract_patterns']:
                    match = re.search(pattern, value_str)
                    if match:
                        try:
                            age = float(match.group(1))
                            if strategy['valid_range'][0] <= age <= strategy['valid_range'][1]:
                                return age
                        except:
                            continue
            
            return None
        
        return series.apply(clean_age)
    
    def _clean_numeric_column(self, series: pd.Series) -> pd.Series:
        """Clean numeric columns handling various formats."""
        strategy = self.cleaning_strategies['numeric']
        
        def clean_numeric(value):
            if pd.isna(value):
                return None
            
            value_str = str(value)
            
            # Remove commas
            if strategy.get('remove_commas', False):
                value_str = value_str.replace(',', '')
            
            # Handle decimal separators
            if strategy.get('handle_decimal_separators'):
                # Replace comma with dot if it's likely a decimal separator
                if ',' in value_str and '.' not in value_str:
                    value_str = value_str.replace(',', '.')
            
            # Try direct conversion
            try:
                return float(value_str)
            except ValueError:
                pass
            
            # Extract from text
            if strategy.get('extract_from_text', False):
                numbers = re.findall(r'[\d.]+', value_str)
                if numbers:
                    try:
                        return float(numbers[0])
                    except:
                        pass
            
            return None
        
        return series.apply(clean_numeric)
    
    def _clean_with_custom_mappings(self, series: pd.Series, mappings: Dict) -> pd.Series:
        """Clean column using custom mappings."""
        def clean_value(value):
            if pd.isna(value):
                return value
            
            value_str = str(value).strip().lower()
            return mappings.get(value_str, value)
        
        return series.apply(clean_value)
    
    def auto_detect_and_clean_amr_data(self, df: pd.DataFrame, 
                                      auto_apply: bool = False) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Automatically detect AMR data columns and apply appropriate cleaning strategies.
        
        Args:
            df: Input dataframe
            auto_apply: Whether to automatically apply cleaning
            
        Returns:
            Tuple of (cleaned dataframe, detection report)
        """
        from .column_utils import normalize_column_name
        
        detection_report = {
            'detected_columns': {},
            'suggested_cleanings': [],
            'confidence_scores': {}
        }
        
        df_cleaned = df.copy()
        
        # Detect organism columns
        for col in df.columns:
            col_normalized = normalize_column_name(col)
            
            # Organism detection
            if any(term in col_normalized for term in ['organism', 'bacteria', 'isolate', 'pathogen']):
                detection_report['detected_columns'][col] = {
                    'type': 'organism',
                    'strategy': 'organism',
                    'confidence': 0.9
                }
                if auto_apply:
                    df_cleaned = self.flexible_clean_column(df_cleaned, col, 'organism')
            
            # Antimicrobial result detection
            elif any(term in col_normalized for term in ['sir', 'susceptibility', 'resistance', 'result']):
                detection_report['detected_columns'][col] = {
                    'type': 'antimicrobial_result',
                    'strategy': 'antimicrobial_result',
                    'confidence': 0.85
                }
                if auto_apply:
                    df_cleaned = self.flexible_clean_column(df_cleaned, col, 'antimicrobial_result')
            
            # Specimen type detection
            elif 'specimen' in col_normalized and 'type' in col_normalized:
                detection_report['detected_columns'][col] = {
                    'type': 'specimen_type',
                    'strategy': 'specimen_type',
                    'confidence': 0.9
                }
                if auto_apply:
                    df_cleaned = self.flexible_clean_column(df_cleaned, col, 'specimen_type')
            
            # Gender detection
            elif any(term in col_normalized for term in ['gender', 'sex']):
                detection_report['detected_columns'][col] = {
                    'type': 'gender',
                    'strategy': 'gender',
                    'confidence': 0.9
                }
                if auto_apply:
                    df_cleaned = self.flexible_clean_column(df_cleaned, col, 'gender')
            
            # Date detection
            elif 'date' in col_normalized:
                detection_report['detected_columns'][col] = {
                    'type': 'date',
                    'strategy': 'date',
                    'confidence': 0.85
                }
                if auto_apply:
                    df_cleaned = self.flexible_clean_column(df_cleaned, col, 'date')
            
            # Age detection
            elif 'age' in col_normalized:
                detection_report['detected_columns'][col] = {
                    'type': 'age',
                    'strategy': 'age',
                    'confidence': 0.85
                }
                if auto_apply:
                    df_cleaned = self.flexible_clean_column(df_cleaned, col, 'age')
        
        return df_cleaned, detection_report
    
    def show_transformation_interface(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Display the transformation interface in Streamlit.
        
        Args:
            df: Input dataframe
            
        Returns:
            Transformed dataframe
        """
        st.write("### Data Transformations")
        
        # Initialize session state
        if 'transformations' not in st.session_state:
            st.session_state['transformations'] = []
        if 'extracted_numbers' not in st.session_state:
            st.session_state['extracted_numbers'] = {}
        if 'transformation_state' not in st.session_state:
            st.session_state['transformation_state'] = {
                'original_columns': list(df.columns),
                'current_columns': list(df.columns),
                'operations_applied': []
            }
        # **CRITICAL FIX**: Initialize processed_data if not exists
        if 'processed_data' not in st.session_state:
            st.session_state['processed_data'] = df.copy()
        
        # **CRITICAL FIX**: Always update processed_data with current df
        st.session_state['processed_data'] = df.copy()
        
        # Update current columns tracking
        st.session_state['transformation_state']['current_columns'] = list(df.columns)
        
        # Show current dataset status at the top
        original_count = len(st.session_state['transformation_state']['original_columns'])
        current_count = len(df.columns)
        operations_count = len(st.session_state['transformation_state'].get('operations_applied', []))
        
        if current_count != original_count or operations_count > 0:
            st.info(f"📊 Dataset Status: {len(df)} rows × {current_count} columns "
                   f"(Started with {original_count} columns, {operations_count} operations applied)")
        
        # Add flexible AMR data cleaning section
        st.write("---")
        st.write("#### 🧹 Flexible AMR Data Cleaning")
        st.markdown("""
        **Automatically detect and clean AMR-specific data columns:**
        - Organism names (standardize variations like "E. coli", "e coli", "E.coli")
        - Antimicrobial results (S/R/I/ND/NM standardization)
        - Specimen types (Blood, Urine, Sputum, etc.)
        - Gender values (M/F/O/U standardization)
        - Date formats (multiple format support)
        - Age values (extract from various text formats)
        """)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            auto_clean_enabled = st.checkbox(
                "Enable automatic AMR data detection and cleaning",
                value=False,
                help="Automatically detect AMR columns and apply appropriate cleaning strategies"
            )
        with col2:
            if st.button("🔍 Detect AMR Columns", help="Detect AMR-specific columns without applying cleaning"):
                cleaned_df, detection_report = self.auto_detect_and_clean_amr_data(df, auto_apply=False)
                st.session_state['amr_detection_report'] = detection_report
                st.success(f"✅ Detected {len(detection_report['detected_columns'])} AMR columns")
                
                # Show detection results
                if detection_report['detected_columns']:
                    with st.expander("📋 View Detected Columns", expanded=True):
                        for col_name, info in detection_report['detected_columns'].items():
                            st.write(f"**{col_name}**: {info['type']} (confidence: {info['confidence']:.0%})")
        
        if auto_clean_enabled:
            if st.button("✨ Apply Automatic Cleaning", type="primary"):
                with st.spinner("Cleaning AMR data..."):
                    cleaned_df, detection_report = self.auto_detect_and_clean_amr_data(df, auto_apply=True)
                    st.session_state['processed_data'] = cleaned_df
                    st.session_state['amr_detection_report'] = detection_report
                    
                    # Track operation
                    if 'operations_applied' not in st.session_state['transformation_state']:
                        st.session_state['transformation_state']['operations_applied'] = []
                    st.session_state['transformation_state']['operations_applied'].append(
                        f"Automatic AMR cleaning ({len(detection_report['detected_columns'])} columns)"
                    )
                    
                    st.success(f"✅ Cleaned {len(detection_report['detected_columns'])} AMR columns")
                    st.rerun()
        
        # Manual column cleaning section
        st.write("---")
        st.write("#### 🎯 Manual Column Cleaning")
        st.markdown("**Select specific columns and cleaning strategies:**")
        
        selected_col = st.selectbox(
            "Select column to clean",
            options=[''] + list(df.columns),
            help="Choose a column to apply specific cleaning strategy"
        )
        
        if selected_col:
            strategy = st.selectbox(
                "Select cleaning strategy",
                options=['organism', 'antimicrobial_result', 'specimen_type', 'gender', 'date', 'age', 'numeric', 'custom'],
                help="Choose the appropriate cleaning strategy for this column"
            )
            
            custom_mappings = None
            if strategy == 'custom':
                st.write("**Define custom mappings (one per line, format: old_value=new_value):**")
                mappings_text = st.text_area(
                    "Custom mappings",
                    height=100,
                    help="Example:\nmale=M\nfemale=F\nother=O"
                )
                if mappings_text:
                    try:
                        custom_mappings = {}
                        for line in mappings_text.strip().split('\n'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                custom_mappings[key.strip().lower()] = value.strip()
                    except:
                        st.error("Invalid mapping format. Use: key=value")
            
            if st.button(f"🧹 Clean '{selected_col}' Column"):
                df = self.flexible_clean_column(df, selected_col, strategy, custom_mappings)
                st.session_state['processed_data'] = df
                st.success(f"✅ Cleaned column '{selected_col}' using {strategy} strategy")
                
                # Show preview
                st.write("**Preview of cleaned column:**")
                st.dataframe(df[[selected_col]].head(10), use_container_width=True)
                st.rerun()
        
        st.write("---")
            
        # Add number extraction section
        st.write("#### Extract Numbers")
        cols_to_extract = st.multiselect(
            "Select columns to extract numbers from",
            options=df.columns,
            help="Select one or more columns to extract numeric values from (e.g., 'S-65' becomes '65')"
        )
        
        preview_button = st.button("Preview Number Extraction")
        if cols_to_extract and preview_button:
            df_copy = df.copy()
            extracted_data = {}
            for col in cols_to_extract:
                extracted_data[col] = self.transformations['text']['extract_numbers'](df_copy[col])
            st.session_state['extracted_numbers'] = extracted_data
            
        # Show preview if we have extracted data
        if st.session_state.get('extracted_numbers'):
            st.write("Preview of extracted numbers:")
            preview_df = df.copy()
            for col, data in st.session_state['extracted_numbers'].items():
                if col in cols_to_extract:  # Only show currently selected columns
                    preview_df[col] = data
            st.dataframe(preview_df[cols_to_extract].head())
            
            if st.button("Apply Number Extraction"):
                # Update the input dataframe with the extracted numbers
                for col in cols_to_extract:
                    if col in st.session_state['extracted_numbers']:
                        df[col] = st.session_state['extracted_numbers'][col]
                
                # **CRITICAL FIX**: Update session state with the modified dataframe
                st.session_state['processed_data'] = df
                
                st.success(f"Extracted numbers from {len(cols_to_extract)} column(s)")
                
                # Track operation
                if 'operations_applied' not in st.session_state['transformation_state']:
                    st.session_state['transformation_state']['operations_applied'] = []
                st.session_state['transformation_state']['operations_applied'].append(
                    f"Number extraction from {len(cols_to_extract)} columns"
                )
                
                # Show preview of updated data
                st.write("##### Data Preview After Number Extraction:")
                from .helpers import prepare_df_for_display
                st.dataframe(prepare_df_for_display(df[cols_to_extract].head(3)), use_container_width=True)
                
                st.session_state['extracted_numbers'] = {}  # Clear the preview
                st.rerun()  # Rerun to update the interface with new values
                
        st.write("---")
        
        # Add empty column removal section
        st.write("#### Remove Empty Columns")
        
        # Show initial column analysis
        total_columns = len(df.columns)
        empty_cols = df.columns[df.isna().all()].tolist()
        non_empty_cols = [col for col in df.columns if col not in empty_cols]
        
        st.write("##### Current Column Analysis")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Columns", total_columns)
        with col2:
            st.metric("Empty Columns", len(empty_cols))
        with col3:
            st.metric("Non-Empty Columns", len(non_empty_cols))
            
        if empty_cols:
            st.write("##### Empty Columns Found:")
            for col in empty_cols:
                st.write(f"- `{col}`")
                
        # Add warning if empty columns contain specific keywords
        important_keywords = ['id', 'date', 'patient', 'specimen', 'result', 'test', 'lab', 'organism', 'antibiotic']
        important_empty_cols = [col for col in empty_cols if any(keyword in col.lower() for keyword in important_keywords)]
        if important_empty_cols:
            st.warning("⚠️ The following empty columns might contain important data. Please verify before removing:", icon="⚠️")
            for col in important_empty_cols:
                st.write(f"- `{col}`")
        
        if st.button("Remove Columns with No Data"):
            if empty_cols:
                # Store original state
                original_df = df.copy()
                
                # Drop the empty columns
                df = df.drop(columns=empty_cols)
                
                # **CRITICAL FIX**: Update session state with the modified dataframe
                st.session_state['processed_data'] = df
                
                # Track operation
                if 'operations_applied' not in st.session_state['transformation_state']:
                    st.session_state['transformation_state']['operations_applied'] = []
                st.session_state['transformation_state']['operations_applied'].append(
                    f"Removed {len(empty_cols)} empty columns"
                )
                
                # Update current columns in transformation state
                st.session_state['transformation_state']['current_columns'] = list(df.columns)
                
                # Show detailed report
                st.success(f"✅ Column Removal Report:")
                st.write("##### Columns Removed:")
                for col in empty_cols:
                    st.write(f"- `{col}`")
                    
                st.write("##### Columns Kept:")
                for col in non_empty_cols:
                    st.write(f"- `{col}`")
                    
                # Show metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Original Columns", len(original_df.columns))
                with col2:
                    st.metric("Removed Columns", len(empty_cols))
                with col3:
                    st.metric("Remaining Columns", len(df.columns))
                
                # Add undo button
                if st.button("Undo Column Removal"):
                    df = original_df
                    
                    # **CRITICAL FIX**: Update session state with the restored dataframe
                    st.session_state['processed_data'] = df
                    
                    # Update current columns in transformation state
                    st.session_state['transformation_state']['current_columns'] = list(df.columns)
                    
                    st.success("✅ Column removal undone")
                    st.rerun()
                    
                # Show preview after removal
                st.write("##### Data Preview After Empty Column Removal:")
                from .helpers import prepare_df_for_display
                st.dataframe(prepare_df_for_display(df.head(3)), use_container_width=True)
            else:
                st.info("No empty columns found")
                
        st.write("---")
        
        # Add manual column deletion section
        st.write("#### Delete Selected Columns")
        st.write("Select specific columns to remove from your dataset.")
        
        # Show current column count
        st.info(f"Current dataset has {len(df.columns)} columns")
        
        # Column selection for deletion
        columns_to_delete = st.multiselect(
            "Select columns to delete",
            options=df.columns.tolist(),
            help="Choose one or more columns to permanently remove from the dataset"
        )
        
        if columns_to_delete:
            # Show preview of what will be removed
            st.write("##### Preview of Selected Columns:")
            preview_data = df[columns_to_delete].head(3)
            st.dataframe(preview_data)
            
            # Show warning for important columns
            important_keywords = ['id', 'date', 'patient', 'specimen', 'result', 'test', 'lab', 'organism', 'antibiotic', 'name']
            important_cols_to_delete = [col for col in columns_to_delete if any(keyword in col.lower() for keyword in important_keywords)]
            
            if important_cols_to_delete:
                st.warning("⚠️ You're about to delete columns that might contain important data:")
                for col in important_cols_to_delete:
                    st.write(f"- `{col}`")
                    
            # Show what will remain
            remaining_columns = [col for col in df.columns if col not in columns_to_delete]
            st.write(f"##### After deletion, {len(remaining_columns)} columns will remain:")
            
            with st.expander("Show remaining columns", expanded=False):
                for col in remaining_columns:
                    st.write(f"- `{col}`")
            
            # Deletion controls
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ Delete Selected Columns", type="primary"):
                    # Store original state for undo
                    original_df_delete = df.copy()
                    
                    # Perform deletion
                    df = df.drop(columns=columns_to_delete)
                    
                    # **CRITICAL FIX**: Update session state with the modified dataframe
                    st.session_state['processed_data'] = df
                    
                    # Show success message with details
                    st.success(f"✅ Successfully deleted {len(columns_to_delete)} column(s)")
                    
                    # Update successful - no debug message needed in production
                    
                    # Track operation
                    if 'operations_applied' not in st.session_state['transformation_state']:
                        st.session_state['transformation_state']['operations_applied'] = []
                    st.session_state['transformation_state']['operations_applied'].append(
                        f"Deleted {len(columns_to_delete)} columns: {', '.join(columns_to_delete)}"
                    )
                    
                    # Update current columns in transformation state
                    st.session_state['transformation_state']['current_columns'] = list(df.columns)
                    
                    # Show deletion summary
                    st.write("##### Deletion Summary:")
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Original Columns", len(original_df_delete.columns))
                    with col_b:
                        st.metric("Deleted Columns", len(columns_to_delete))
                    with col_c:
                        st.metric("Remaining Columns", len(df.columns))
                    
                    # List deleted columns
                    st.write("**Deleted Columns:**")
                    for col in columns_to_delete:
                        st.write(f"- `{col}`")
                    
                    # Store deletion history in session state for undo
                    if 'deletion_history' not in st.session_state:
                        st.session_state['deletion_history'] = []
                    st.session_state['deletion_history'].append({
                        'deleted_columns': columns_to_delete,
                        'original_df': original_df_delete
                    })
                    
                    st.rerun()
            
            with col2:
                # Undo functionality
                if 'deletion_history' in st.session_state and st.session_state['deletion_history']:
                    if st.button("↶ Undo Last Deletion"):
                        last_deletion = st.session_state['deletion_history'].pop()
                        df = last_deletion['original_df']
                        
                        # **CRITICAL FIX**: Update session state with the restored dataframe
                        st.session_state['processed_data'] = df
                        
                        # Update current columns in transformation state
                        st.session_state['transformation_state']['current_columns'] = list(df.columns)
                        
                        st.success(f"✅ Undid deletion of {len(last_deletion['deleted_columns'])} column(s)")
                        st.rerun()
        
        # Show current data preview after column operations
        if len(df.columns) > 0:
            st.write("##### Current Data Preview (After Column Operations)")
            from .helpers import prepare_df_for_display
            st.dataframe(prepare_df_for_display(df.head(3)), use_container_width=True)
            st.info(f"Current dataset: {len(df)} rows × {len(df.columns)} columns")
        
        st.write("---")
            
        # Add age standardization section
        st.write("#### Age Standardization")
        if st.checkbox("Standardize age values to years"):
            age_column = st.selectbox(
                "Select age column",
                options=df.columns,
                help="Select the column containing age values to standardize"
            )
            if age_column:
                df = self.age_transformer.show_age_standardization_interface(df, age_column)
                
                # **CRITICAL FIX**: Update session state with age-standardized data
                st.session_state['processed_data'] = df
        
        # Add transformation button
        if st.button("Add Transformation"):
            st.session_state['transformations'].append({})
        
        # Create the final transformed dataframe that includes ALL previous changes
        # This includes: number extractions, column deletions, empty column removals, and age standardization
        # **CRITICAL FIX**: Use the updated session state data instead of local df
        transformed_df = st.session_state['processed_data'].copy()
        
        # Ensure that all columns referenced in transformations still exist after deletions
        valid_transformations = []
        for transform_dict in st.session_state.get('transformations', []):
            # Only keep transformations for columns that still exist
            if 'column' in transform_dict and transform_dict['column'] in transformed_df.columns:
                valid_transformations.append(transform_dict)
        
        # Update session state with valid transformations only
        if len(valid_transformations) != len(st.session_state.get('transformations', [])):
            st.session_state['transformations'] = valid_transformations
            st.info("Some transformations were removed because their target columns were deleted.")
            
        # Apply existing transformations
        for i, transform_dict in enumerate(st.session_state['transformations']):
            st.write(f"#### Transformation {i + 1}")
            
            # Create columns for transformation controls
            col1, col2 = st.columns(2)
            
            with col1:
                column = st.selectbox(
                    "Column",
                    options=transformed_df.columns,  # Use transformed_df columns (reflects deletions)
                    key=f"col_{i}"
                )
            
            with col2:
                transform_type = st.selectbox(
                    "Transformation",
                    options=self._get_transformation_types(transformed_df[column].dtype) if column else [],
                    key=f"type_{i}"
                )
            
            # Additional parameters for certain transformations
            params = self._get_transformation_params(transform_type or "", i)
            
            # Apply transformation
            if column and transform_type:
                transformed_df = self._apply_transformation(
                    transformed_df,
                    column,
                    transform_type,
                    params
                )
                
                # **CRITICAL FIX**: Update session state with transformed data
                st.session_state['processed_data'] = transformed_df
                
                # Track operation
                if 'operations_applied' not in st.session_state['transformation_state']:
                    st.session_state['transformation_state']['operations_applied'] = []
                
                # Check if this operation is already tracked
                operation_desc = f"Applied {transform_type} to {column}"
                if operation_desc not in st.session_state['transformation_state']['operations_applied']:
                    st.session_state['transformation_state']['operations_applied'].append(operation_desc)
                
                # Show immediate preview of the transformation
                st.write(f"##### Preview after {transform_type} on {column}:")
                from .helpers import prepare_df_for_display
                st.dataframe(prepare_df_for_display(transformed_df[[column]].head(3)), use_container_width=True)
            
            # Remove transformation button
            if st.button("Remove Transformation", key=f"remove_{i}"):
                st.session_state['transformations'].pop(i)
                st.rerun()
        
        # Show transformation results
        st.write("### 📊 Final Transformed Data Preview")
        st.write("This is the final dataset that will be used for export and validation:")
        
        # Show operations applied
        if 'operations_applied' in st.session_state.get('transformation_state', {}):
            with st.expander("📋 Applied Operations", expanded=False):
                for i, op in enumerate(st.session_state['transformation_state']['operations_applied'], 1):
                    st.markdown(f"{i}. {op}")
        
        from .helpers import prepare_df_for_display
        
        # Show column comparison if deletions occurred
        original_cols = st.session_state['transformation_state']['original_columns']
        current_cols = list(transformed_df.columns)
        
        if len(original_cols) != len(current_cols):
            st.write("#### Column Changes:")
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.write("**Original Columns:**")
                deleted_cols = [col for col in original_cols if col not in current_cols]
                for col in original_cols:
                    if col in deleted_cols:
                        st.write(f"~~{col}~~ (deleted)")
                    else:
                        st.write(f"✓ {col}")
            
            with col_b:
                st.write("**Current Columns:**")
                for col in current_cols:
                    st.write(f"✓ {col}")
        
        # Show the actual data preview
        st.dataframe(prepare_df_for_display(transformed_df.head(10)), use_container_width=True)
        
        # Add expandable full column view
        with st.expander("View All Columns", expanded=False):
            col_info = []
            for i, col in enumerate(transformed_df.columns):
                dtype = str(transformed_df[col].dtype)
                non_null = transformed_df[col].notna().sum()
                col_info.append({
                    'Column': col,
                    'Data Type': dtype,
                    'Non-Null Count': non_null,
                    'Null Count': len(transformed_df) - non_null
                })
            
            col_df = pd.DataFrame(col_info)
            st.dataframe(col_df, use_container_width=True)
        
        # Provide comprehensive summary of all applied transformations
        st.write("### Transformation Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Dataset Changes:**")
            original_cols = len(st.session_state['transformation_state']['original_columns'])
            current_cols = len(transformed_df.columns)
            st.metric("Original Columns", original_cols)
            st.metric("Final Columns", current_cols, delta=current_cols - original_cols)
            st.metric("Total Rows", len(transformed_df))
        
        with col2:
            st.write("**Applied Operations:**")
            # Count applied transformations
            applied_transformations = len([t for t in st.session_state.get('transformations', []) if t])
            st.metric("Data Transformations", applied_transformations)
            
            # Check if any column deletions were made
            deletion_history = st.session_state.get('deletion_history', [])
            total_deleted = sum(len(d.get('deleted_columns', [])) for d in deletion_history)
            st.metric("Deleted Columns", total_deleted)
            
            # Check for number extractions
            extracted_count = len(st.session_state.get('extracted_numbers', {}))
            if extracted_count == 0:
                # Check if any were applied previously (session state cleared after apply)
                extracted_count = "Applied" if any(col for col in transformed_df.columns) else 0
            st.metric("Number Extractions", extracted_count if isinstance(extracted_count, str) else extracted_count)
        
        with col3:
            st.write("**Data Types:**")
            # Show data type summary
            numeric_cols = len(transformed_df.select_dtypes(include=['number']).columns)
            text_cols = len(transformed_df.select_dtypes(include=['object']).columns)
            datetime_cols = len(transformed_df.select_dtypes(include=['datetime']).columns)
            st.metric("Numeric Columns", numeric_cols)
            st.metric("Text Columns", text_cols)
            st.metric("Date Columns", datetime_cols)
        
        # Final verification message
        st.success("✅ All transformations have been applied to the final dataset. This is the data that will be exported.")
        
        # **CRITICAL FIX**: Update session state with final transformed data and return it
        st.session_state['processed_data'] = transformed_df
        return transformed_df
    
    def _get_transformation_types(self, dtype) -> List[str]:
        """
        Get appropriate transformation types for a column's data type.
        
        Args:
            dtype: Column data type
            
        Returns:
            List of applicable transformations
        """
        if pd.api.types.is_numeric_dtype(dtype):
            return list(self.transformations['number'].keys())
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return list(self.transformations['date'].keys())
        else:
            return list(self.transformations['text'].keys())
    
    def _get_transformation_params(self, transform_type: str, index: int) -> Dict[str, Any]:
        """
        Get additional parameters for transformations that require them.
        
        Args:
            transform_type: Type of transformation
            index: Index for unique keys
            
        Returns:
            Dictionary of parameters
        """
        params = {}
        
        if transform_type == 'round':
            params['decimals'] = st.number_input(
                "Decimal Places",
                min_value=0,
                max_value=10,
                value=2,
                key=f"param_{index}"
            )
        
        return params
    
    def _apply_transformation(
        self,
        df: pd.DataFrame,
        column: str,
        transform_type: str,
        params: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Apply transformation to dataframe.
        
        Args:
            df: Input dataframe
            column: Column to transform
            transform_type: Type of transformation
            params: Additional parameters
            
        Returns:
            Transformed dataframe
        """
        transformed_df = df.copy()
        
        try:
            if pd.api.types.is_numeric_dtype(df[column].dtype):
                transform_func = self.transformations['number'][transform_type]
                if transform_type == 'round':
                    transformed_df[column] = transform_func(df[column], params['decimals'])
                else:
                    transformed_df[column] = transform_func(df[column])
            
            elif pd.api.types.is_datetime64_any_dtype(df[column].dtype):
                transform_func = self.transformations['date'][transform_type]
                transformed_df[column] = transform_func(df[column])
            
            else:
                transform_func = self.transformations['text'][transform_type]
                transformed_df[column] = transform_func(df[column].astype(str))
            
            st.success(f"Applied {transform_type} transformation to {column}")
            
        except Exception as e:
            st.error(f"Error applying transformation: {str(e)}")
        
        return transformed_df
