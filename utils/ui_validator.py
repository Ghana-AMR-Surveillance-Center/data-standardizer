"""
UI/UX Validation and Best Practices Module
Ensures user-friendly interfaces and workflows following best practices
"""

import streamlit as st
from typing import Dict, List, Any, Optional
import pandas as pd

class UIValidator:
    """
    Validates and improves UI/UX following best practices:
    - Clear error messages with actionable guidance
    - Loading states for all operations
    - Help tooltips and contextual help
    - Consistent styling and layout
    - Accessibility considerations
    - User feedback and confirmation
    """
    
    @staticmethod
    def show_help_tooltip(text: str, icon: str = "❓"):
        """Show help tooltip icon with hover text"""
        st.markdown(f'<span title="{text}">{icon}</span>', unsafe_allow_html=True)
    
    @staticmethod
    def show_contextual_help(context: str, help_text: str):
        """Show contextual help based on current workflow step"""
        with st.expander(f"ℹ️ Help: {context}", expanded=False):
            st.markdown(help_text)
    
    @staticmethod
    def validate_file_upload(file, max_size_mb: float = 100) -> Dict[str, Any]:
        """
        Validate uploaded file with user-friendly error messages
        
        Returns:
            Dict with 'valid', 'errors', 'warnings', 'file_info'
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'file_info': {}
        }
        
        if file is None:
            return result
        
        # Check file size
        file_size_mb = len(file.getvalue()) / (1024 * 1024)
        result['file_info'] = {
            'name': file.name,
            'size_mb': round(file_size_mb, 2),
            'type': file.type
        }
        
        if file_size_mb > max_size_mb:
            result['valid'] = False
            result['errors'].append(
                f"File size ({file_size_mb:.1f} MB) exceeds maximum allowed size ({max_size_mb} MB). "
                f"Please split your data into smaller files or contact support for assistance."
            )
        
        # Check file type
        allowed_types = ['text/csv', 'application/vnd.ms-excel', 
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
        if file.type not in allowed_types:
            result['warnings'].append(
                f"File type '{file.type}' may not be supported. "
                f"Please use CSV or Excel (.xlsx, .xls) files for best results."
            )
        
        return result
    
    @staticmethod
    def show_operation_feedback(operation: str, status: str, message: str, 
                               details: Optional[str] = None, duration: int = 3):
        """Show operation feedback with appropriate styling"""
        icons = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'processing': '⏳'
        }
        
        icon = icons.get(status, 'ℹ️')
        
        if status == 'success':
            st.success(f"{icon} **{operation}**: {message}")
        elif status == 'error':
            st.error(f"{icon} **{operation}**: {message}")
            if details:
                with st.expander("🔍 Error Details"):
                    st.code(details)
        elif status == 'warning':
            st.warning(f"{icon} **{operation}**: {message}")
        elif status == 'processing':
            with st.spinner(f"{icon} {operation}: {message}"):
                pass
        else:
            st.info(f"{icon} **{operation}**: {message}")
        
        if details and status != 'error':
            st.caption(details)
    
    @staticmethod
    def show_data_preview_with_guidance(df: pd.DataFrame, title: str = "Data Preview"):
        """Show data preview with helpful guidance"""
        st.markdown(f"### {title}")
        
        # Show guidance
        st.info("""
        **Preview Tips:**
        - Review the first few rows to ensure data loaded correctly
        - Check for obvious data quality issues (missing values, incorrect formats)
        - Verify column names match your expectations
        """)
        
        # Show preview
        st.dataframe(df.head(10), use_container_width=True)
        
        # Show summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", len(df))
        with col2:
            st.metric("Total Columns", len(df.columns))
        with col3:
            missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            st.metric("Missing Data", f"{missing_pct:.1f}%")
    
    @staticmethod
    def confirm_action(message: str, action_label: str = "Confirm", 
                      cancel_label: str = "Cancel") -> bool:
        """Show confirmation dialog for critical actions"""
        col1, col2 = st.columns([3, 1])
        with col1:
            st.warning(message)
        with col2:
            if st.button(action_label, type="primary", use_container_width=True):
                return True
            if st.button(cancel_label, use_container_width=True):
                return False
        return False
    
    @staticmethod
    def show_workflow_guidance(workflow_type: str):
        """Show contextual guidance for current workflow"""
        guidance = {
            'single': """
            **Single File Workflow Guide:**
            1. **Upload**: Select your data file (CSV or Excel)
            2. **Map** (Optional): Rename columns to standard names
            3. **Transform**: Clean and standardize data values
            4. **Validate**: Check data quality and completeness
            5. **Export**: Download processed data
            
            **Tips:**
            - Start with a small sample file to test the workflow
            - Review data quality assessment before exporting
            - Use auto-fix options to improve data quality automatically
            """,
            'multiple': """
            **Multiple Files Workflow Guide:**
            1. **Upload**: Select multiple files to merge
            2. **Merge**: Files are automatically combined with smart column matching
            3. **Transform**: Clean and standardize merged data
            4. **Validate**: Check merged data quality
            5. **Export**: Download unified dataset
            
            **Tips:**
            - Files should have similar structure for best results
            - Column names will be automatically matched
            - Review merge statistics to ensure correct combination
            """,
            'glass': """
            **GLASS Preparation Wizard Guide:**
            This wizard guides you through preparing AMR data for GLASS submission.
            
            **What to expect:**
            - Automatic data cleaning and standardization
            - GLASS format validation
            - Quality assessment and recommendations
            - Ready-to-submit data export
            
            **Requirements:**
            - Organism names
            - Specimen types
            - Specimen dates
            - Patient age and gender
            - Antimicrobial susceptibility results
            """,
            'whonet': """
            **WHONET Preparation Wizard Guide:**
            This wizard prepares your AMR data for WHONET import.
            
            **What to expect:**
            - Automatic format conversion
            - WHONET-compatible standardization
            - Quality validation
            - Import-ready data export
            
            **Requirements:**
            - Organism identification
            - Antimicrobial test results
            - Patient/specimen information
            """
        }
        
        help_text = guidance.get(workflow_type, "Workflow guidance not available.")
        
        with st.expander("📖 Workflow Guide", expanded=False):
            st.markdown(help_text)
    
    @staticmethod
    def show_accessible_labels():
        """Add accessibility improvements"""
        st.markdown("""
        <style>
        /* Accessibility improvements */
        .stButton > button {
            min-height: 2.5rem;
            font-size: 1rem;
        }
        
        .stTextInput > label,
        .stSelectbox > label,
        .stFileUploader > label {
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        /* High contrast for important elements */
        .stAlert {
            border-left: 4px solid;
        }
        
        /* Focus indicators */
        .stButton > button:focus,
        .stTextInput > div > input:focus {
            outline: 2px solid #0066cc;
            outline-offset: 2px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def validate_dataframe_for_processing(df: pd.DataFrame) -> Dict[str, Any]:
        """Validate dataframe before processing with user-friendly messages"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        if df is None or df.empty:
            result['valid'] = False
            result['errors'].append(
                "Data file is empty. Please upload a file with data."
            )
            return result
        
        # Check for minimum rows
        if len(df) < 1:
            result['valid'] = False
            result['errors'].append(
                "Data file must contain at least one row of data."
            )
        
        # Check for minimum columns
        if len(df.columns) < 1:
            result['valid'] = False
            result['errors'].append(
                "Data file must contain at least one column."
            )
        
        # Check for excessive missing data
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        if missing_pct > 50:
            result['warnings'].append(
                f"High percentage of missing data ({missing_pct:.1f}%). "
                "Consider reviewing your data source or using data imputation."
            )
        
        # Check for duplicate rows
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            result['warnings'].append(
                f"Found {duplicate_count} duplicate rows. "
                "Consider removing duplicates before processing."
            )
        
        # Suggestions
        if 'Organism' not in df.columns and any('organism' in col.lower() for col in df.columns):
            result['suggestions'].append(
                "Found potential organism column. Consider mapping it to 'Organism' for AMR analysis."
            )
        
        return result

# Global UI validator instance
ui_validator = UIValidator()

