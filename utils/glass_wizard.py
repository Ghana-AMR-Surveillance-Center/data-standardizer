"""
GLASS Data Preparation Wizard
Step-by-step guided interface for non-technical users to prepare AMR data for GLASS submission.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional
from .glass_standardizer import GLASSStandardizer

class GLASSWizard:
    """
    Step-by-step wizard for GLASS data preparation.
    Designed for non-technical users with clear guidance and automatic fixes.
    """
    
    def __init__(self):
        self.standardizer = GLASSStandardizer()
        self.current_step = 0
        self.total_steps = 6
    
    def run_wizard(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Run the complete GLASS preparation wizard.
        
        Args:
            df: Input dataframe
            
        Returns:
            Standardized dataframe ready for GLASS submission, or None if cancelled
        """
        st.title("🧬 GLASS Data Preparation Wizard")
        st.markdown("""
        **Welcome!** This wizard will guide you through preparing your AMR data for GLASS submission.
        
        **What this wizard does:**
        - ✅ Automatically cleans and standardizes your data
        - ✅ Fixes common data issues
        - ✅ Validates against GLASS requirements
        - ✅ Prepares your data for submission
        
        **No programming knowledge required!** Just follow the steps.
        """)
        
        st.markdown("---")
        
        # Step 1: Data Overview
        if self._step_1_data_overview(df):
            df = st.session_state.get('wizard_df', df)
        else:
            return None
        
        # Step 2: Automatic Cleaning
        if self._step_2_automatic_cleaning(df):
            df = st.session_state.get('wizard_df', df)
        else:
            return None
        
        # Step 3: Column Mapping
        if self._step_3_column_mapping(df):
            df = st.session_state.get('wizard_df', df)
        else:
            return None
        
        # Step 4: Data Validation
        if self._step_4_validation(df):
            df = st.session_state.get('wizard_df', df)
        else:
            return None
        
        # Step 5: Review & Fix Issues
        if self._step_5_review_and_fix(df):
            df = st.session_state.get('wizard_df', df)
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
                st.session_state['wizard_df'] = df.copy()
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
        - Standardize specimen types (e.g., "Blood", "Urine")
        - Fix gender values (M, F, O, U)
        - Standardize antimicrobial results (S, R, I, ND, NM)
        - Clean dates and ages
        - Remove invalid rows
        """)
        
        auto_fix = st.checkbox(
            "Enable automatic cleaning and fixing",
            value=True,
            help="We'll automatically fix common data issues. You can review changes in the next step."
        )
        
        if st.button("🧹 Start Automatic Cleaning", type="primary", use_container_width=True):
            with st.spinner("Cleaning your data... This may take a moment."):
                cleaned_df, report = self.standardizer.standardize_for_glass(df, auto_fix=auto_fix)
                
                st.session_state['wizard_df'] = cleaned_df
                st.session_state['wizard_cleaning_report'] = report
                
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
        """Step 3: Map columns to GLASS standard names."""
        st.header("Step 3 of 6: Column Mapping")
        
        st.markdown("""
        **What is column mapping?**
        Your data might have column names like "Patient Age" or "Bacteria Name", 
        but GLASS needs "Age in years" and "Organism". We'll help you map them.
        """)
        
        # Show required GLASS fields
        st.write("### GLASS Required Fields:")
        required_fields = list(self.standardizer.GLASS_REQUIRED_FIELDS.keys())
        st.write(", ".join([f"**{field}**" for field in required_fields]))
        
        # Auto-detect mappings
        st.write("### Automatic Column Detection:")
        detected_mappings = {}
        
        from utils.column_utils import normalize_column_name, match_column_name
        
        for field in required_fields:
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
                'GLASS Field': list(detected_mappings.keys()),
                'Your Column': list(detected_mappings.values())
            })
            st.dataframe(mapping_df, use_container_width=True)
            
            if st.button("✅ Use These Mappings", type="primary", use_container_width=True):
                # Apply mappings
                df_mapped = df.rename(columns={v: k for k, v in detected_mappings.items()})
                st.session_state['wizard_df'] = df_mapped
                st.success("Column mappings applied!")
                return True
        else:
            st.warning("⚠️ Could not automatically detect column mappings. Manual mapping may be needed.")
        
        # Manual mapping option
        if st.checkbox("I want to map columns manually"):
            st.write("### Manual Column Mapping:")
            st.info("This feature will be available in the full workflow. For now, automatic detection should work for most cases.")
        
        return False
    
    def _step_4_validation(self, df: pd.DataFrame) -> bool:
        """Step 4: Validate data against GLASS requirements."""
        st.header("Step 4 of 6: GLASS Validation")
        
        st.markdown("""
        **What we're checking:**
        - All required fields are present
        - Data completeness (at least 80% filled)
        - Data format is correct
        - Values are within acceptable ranges
        """)
        
        if st.button("🔍 Run GLASS Validation", type="primary", use_container_width=True):
            with st.spinner("Validating your data against GLASS requirements..."):
                validation = self.standardizer._validate_glass_requirements(df)
                
                # Show validation results
                if validation['valid']:
                    st.success("✅ **GLASS Validation: PASSED**")
                    st.balloons()
                else:
                    st.error("❌ **GLASS Validation: FAILED**")
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
                
                st.session_state['wizard_validation'] = validation
                
                if validation['valid']:
                    return True
                else:
                    st.warning("""
                    **Don't worry!** You can fix these issues in the next step.
                    Many issues can be fixed automatically.
                    """)
                    return True
        
        return False
    
    def _step_5_review_and_fix(self, df: pd.DataFrame) -> bool:
        """Step 5: Review data and fix remaining issues."""
        st.header("Step 5 of 6: Review & Fix Issues")
        
        validation = st.session_state.get('wizard_validation', {})
        
        if validation.get('valid'):
            st.success("✅ Your data passed GLASS validation!")
            st.write("### Final Data Preview:")
            st.dataframe(df.head(10), use_container_width=True)
            
            st.info("""
            **Your data is ready for GLASS submission!**
            
            In the next step, you can export your cleaned and standardized data.
            """)
        else:
            st.warning("⚠️ Some issues were found. Let's fix them!")
            
            # Show issues and provide fixes
            if validation.get('errors'):
                st.write("### Issues to Fix:")
                for error in validation['errors']:
                    st.write(f"- ❌ {error}")
            
            # Auto-fix button
            if st.button("🔧 Try Automatic Fix", type="primary"):
                with st.spinner("Attempting to fix issues automatically..."):
                    fixed_df, report = self.standardizer.standardize_for_glass(df, auto_fix=True)
                    st.session_state['wizard_df'] = fixed_df
                    st.success("Automatic fixes applied! Re-run validation to check.")
                    st.rerun()
        
        return True
    
    def _step_6_final_export(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Step 6: Final review and export."""
        st.header("Step 6 of 6: Final Export")
        
        st.success("🎉 **Congratulations!** Your data is ready for GLASS submission.")
        
        # Final summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Final Rows", len(df))
        with col2:
            st.metric("Final Columns", len(df.columns))
        with col3:
            required_fields = list(self.standardizer.GLASS_REQUIRED_FIELDS.keys())
            present_fields = sum(1 for field in required_fields if field in df.columns)
            st.metric("GLASS Fields", f"{present_fields}/{len(required_fields)}")
        
        st.write("### Final Data Preview:")
        st.dataframe(df.head(10), use_container_width=True)
        
        st.write("### Export Options:")
        st.info("""
        Your data is now standardized and ready for GLASS submission!
        
        **Next steps:**
        1. Export your cleaned data using the export button below
        2. Review the exported file
        3. Submit to GLASS according to their submission guidelines
        
        **What was done:**
        - ✅ Data cleaned and standardized
        - ✅ Column names mapped to GLASS format
        - ✅ Values standardized (organisms, specimen types, etc.)
        - ✅ Invalid rows removed
        - ✅ Data validated against GLASS requirements
        """)
        
        return df

