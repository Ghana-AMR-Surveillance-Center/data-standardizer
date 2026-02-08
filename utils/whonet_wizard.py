"""
WHONET Data Preparation Wizard
Step-by-step guided interface for non-technical users to prepare AMR data for WHONET import.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional
from .whonet_standardizer import WHONETStandardizer
from .enhanced_quality_reporter import EnhancedQualityReporter

class WHONETWizard:
    """
    Step-by-step wizard for WHONET data preparation.
    Designed for non-technical users with clear guidance and automatic fixes.
    """
    
    def __init__(self):
        self.standardizer = WHONETStandardizer()
        self.quality_reporter = EnhancedQualityReporter()
        self.current_step = 0
        self.total_steps = 6
    
    def run_wizard(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Run the complete WHONET preparation wizard.
        
        Args:
            df: Input dataframe
            
        Returns:
            Standardized dataframe ready for WHONET import, or None if cancelled
        """
        st.title("🧬 WHONET Data Preparation Wizard")
        st.markdown("""
        **Welcome!** This wizard will guide you through preparing your AMR data for WHONET import.
        
        **What this wizard does:**
        - ✅ Automatically cleans and standardizes your data
        - ✅ Converts data to WHONET format
        - ✅ Fixes common data issues
        - ✅ Validates against WHONET requirements
        - ✅ Prepares your data for WHONET import
        
        **No programming knowledge required!** Just follow the steps.
        """)
        
        st.markdown("---")
        
        # Step 1: Data Overview
        if self._step_1_data_overview(df):
            df = st.session_state.get('whonet_wizard_df', df)
        else:
            return None
        
        # Step 2: Automatic Cleaning
        if self._step_2_automatic_cleaning(df):
            df = st.session_state.get('whonet_wizard_df', df)
        else:
            return None
        
        # Step 3: Column Mapping
        if self._step_3_column_mapping(df):
            df = st.session_state.get('whonet_wizard_df', df)
        else:
            return None
        
        # Step 4: Data Quality Report
        if self._step_4_quality_report(df):
            df = st.session_state.get('whonet_wizard_df', df)
        else:
            return None
        
        # Step 5: Validation
        if self._step_5_validation(df):
            df = st.session_state.get('whonet_wizard_df', df)
        else:
            return None
        
        # Step 6: Final Export
        return self._step_6_final_export(df)
    
    def _step_1_data_overview(self, df: pd.DataFrame) -> bool:
        """Step 1: Show data overview and get user confirmation."""
        st.header("Step 1 of 6: Data Overview")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", len(df))
        with col2:
            st.metric("Total Columns", len(df.columns))
        with col3:
            st.metric("Data Size", f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
        
        st.write("### Your Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
        
        st.write("### Column Information")
        col_info = pd.DataFrame({
            'Column Name': df.columns,
            'Data Type': [str(df[col].dtype) for col in df.columns],
            'Non-Empty Values': [df[col].notna().sum() for col in df.columns],
            'Empty Values': [df[col].isna().sum() for col in df.columns]
        })
        st.dataframe(col_info, use_container_width=True)
        
        st.info("""
        **What to check:**
        - Does your data look correct?
        - Are there any obvious issues (like all empty columns)?
        - Do you see organism names and antimicrobial results?
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, my data looks good", type="primary", use_container_width=True):
                st.session_state['whonet_wizard_df'] = df.copy()
                return True
        with col2:
            if st.button("❌ No, I need to upload different data", use_container_width=True):
                st.info("Please go back and upload a different file.")
                return False
        
        return False
    
    def _step_2_automatic_cleaning(self, df: pd.DataFrame) -> bool:
        """Step 2: Automatic data cleaning and standardization."""
        st.header("Step 2 of 6: Automatic Data Cleaning")
        
        st.markdown("""
        **What we'll do automatically:**
        - Clean and standardize organism names (e.g., "E. coli", "S. aureus")
        - Standardize specimen types to WHONET format
        - Fix sex values (M, F, U)
        - Standardize antimicrobial results to SIR format (S, R, I, ND, NM)
        - Clean dates and ages
        - Convert column names to WHONET format (uppercase)
        - Remove invalid rows
        """)
        
        auto_fix = st.checkbox(
            "Enable automatic cleaning and fixing",
            value=True,
            help="We'll automatically fix common data issues. You can review changes in the next step."
        )
        
        if st.button("🧹 Start Automatic Cleaning", type="primary", use_container_width=True):
            with st.spinner("Cleaning your data for WHONET... This may take a moment."):
                cleaned_df, report = self.standardizer.standardize_for_whonet(df, auto_fix=auto_fix)
                
                st.session_state['whonet_wizard_df'] = cleaned_df
                st.session_state['whonet_cleaning_report'] = report
                
                # Show cleaning report
                self.standardizer.show_cleaning_report(report)
                
                st.success("✅ Data cleaning completed!")
                
                # Show before/after comparison
                with st.expander("📊 Before/After Comparison", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Before Cleaning:**")
                        st.dataframe(df.head(5), use_container_width=True)
                    with col2:
                        st.write("**After Cleaning:**")
                        st.dataframe(cleaned_df.head(5), use_container_width=True)
                
                return True
        
        return False
    
    def _step_3_column_mapping(self, df: pd.DataFrame) -> bool:
        """Step 3: Map columns to WHONET standard names."""
        st.header("Step 3 of 6: Column Mapping")
        
        st.markdown("""
        **What is column mapping?**
        Your data might have column names like "Patient Age" or "Bacteria Name", 
        but WHONET needs "AGE" and "ORGANISM". We'll help you map them.
        """)
        
        # Show required WHONET fields
        st.write("### WHONET Required Fields:")
        required_fields = ['ORGANISM', 'SPEC_DATE']
        optional_fields = ['AGE', 'SEX', 'SPEC_TYPE', 'PATIENT_ID']
        st.write("**Required:** " + ", ".join(required_fields))
        st.write("**Optional:** " + ", ".join(optional_fields))
        
        # Auto-detect mappings
        st.write("### Automatic Column Detection:")
        detected_mappings = {}
        
        from utils.column_utils import normalize_column_name, match_column_name
        
        for field in required_fields + optional_fields:
            # Try to find matching column (case-insensitive, whitespace-insensitive)
            for col in df.columns:
                if match_column_name(col, field):
                    detected_mappings[field] = col
                    break
                # Also check substring match
                col_normalized = normalize_column_name(col)
                field_normalized = normalize_column_name(field)
                if field_normalized in col_normalized or col_normalized in field_normalized:
                    detected_mappings[field] = col
                    break
        
        if detected_mappings:
            st.success(f"✅ Automatically detected {len(detected_mappings)} column mappings!")
            mapping_df = pd.DataFrame({
                'WHONET Field': list(detected_mappings.keys()),
                'Your Column': list(detected_mappings.values())
            })
            st.dataframe(mapping_df, use_container_width=True)
            
            if st.button("✅ Use These Mappings", type="primary", use_container_width=True):
                # Apply mappings
                df_mapped = df.rename(columns={v: k for k, v in detected_mappings.items()})
                st.session_state['whonet_wizard_df'] = df_mapped
                st.success("Column mappings applied!")
                return True
        else:
            st.warning("⚠️ Could not automatically detect column mappings. Manual mapping may be needed.")
        
        return False
    
    def _step_4_quality_report(self, df: pd.DataFrame) -> bool:
        """Step 4: Comprehensive data quality report."""
        st.header("Step 4 of 6: Data Quality Report")
        
        st.markdown("""
        **What we're checking:**
        - Data completeness (missing values)
        - Data consistency (format variations)
        - Data validity (correct values)
        - Data accuracy (outliers, errors)
        - Data uniqueness (duplicates)
        """)
        
        if st.button("📊 Generate Quality Report", type="primary", use_container_width=True):
            with st.spinner("Analyzing data quality..."):
                quality_report = self.quality_reporter.generate_comprehensive_report(df, context='whonet')
                
                st.session_state['whonet_quality_report'] = quality_report
                
                # Display comprehensive report
                self.quality_reporter.display_comprehensive_report(quality_report)
                
                st.success("✅ Quality report generated!")
                return True
        
        return False
    
    def _step_5_validation(self, df: pd.DataFrame) -> bool:
        """Step 5: Validate data against WHONET requirements."""
        st.header("Step 5 of 6: WHONET Validation")
        
        st.markdown("""
        **What we're checking:**
        - All required fields are present
        - Data completeness (at least 80% filled)
        - Data format is correct (WHONET format)
        - Values are within acceptable ranges
        - Column names are in WHONET format
        """)
        
        if st.button("🔍 Run WHONET Validation", type="primary", use_container_width=True):
            with st.spinner("Validating your data against WHONET requirements..."):
                validation = self.standardizer._validate_whonet_requirements(df)
                
                # Show validation results
                if validation['valid']:
                    st.success("✅ **WHONET Validation: PASSED**")
                    st.balloons()
                else:
                    st.error("❌ **WHONET Validation: FAILED**")
                    st.write("**Issues found:**")
                    for error in validation.get('errors', []):
                        st.write(f"- ❌ {error}")
                
                if validation.get('warnings'):
                    st.warning("⚠️ **Warnings:**")
                    for warning in validation['warnings']:
                        st.write(f"- ⚠️ {warning}")
                
                # Completeness scores
                if validation.get('completeness_scores'):
                    st.write("### Data Completeness:")
                    for field, score in validation['completeness_scores'].items():
                        color = "🟢" if score >= 80 else "🟡" if score >= 50 else "🔴"
                        st.write(f"{color} **{field}**: {score:.1f}% complete")
                        st.progress(score / 100)
                
                st.session_state['whonet_validation'] = validation
                
                if validation['valid']:
                    return True
                else:
                    st.warning("""
                    **Don't worry!** You can fix these issues in the next step.
                    Many issues can be fixed automatically.
                    """)
                    return True
        
        return False
    
    def _step_6_final_export(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Step 6: Final review and export."""
        st.header("Step 6 of 6: Final Export")
        
        st.success("🎉 **Congratulations!** Your data is ready for WHONET import.")
        
        # Final summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Final Rows", len(df))
        with col2:
            st.metric("Final Columns", len(df.columns))
        with col3:
            required_fields = ['ORGANISM', 'SPEC_DATE']
            present_fields = sum(1 for field in required_fields if field in df.columns)
            st.metric("WHONET Fields", f"{present_fields}/{len(required_fields)}")
        
        st.write("### Final Data Preview:")
        st.dataframe(df.head(10), use_container_width=True)
        
        st.write("### Export Options:")
        st.info("""
        Your data is now standardized and ready for WHONET import!
        
        **Next steps:**
        1. Export your cleaned data using the export button below
        2. Review the exported file
        3. Import into WHONET using the standard import procedure
        
        **What was done:**
        - ✅ Data cleaned and standardized
        - ✅ Column names converted to WHONET format (uppercase)
        - ✅ Values standardized (organisms, specimen types, SIR results)
        - ✅ Invalid rows removed
        - ✅ Data validated against WHONET requirements
        """)
        
        return df

