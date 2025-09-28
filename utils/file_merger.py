"""
File Merger Module
Handles merging of multiple Excel files with column mapping.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd
from typing import Any, Dict, List, Tuple, Optional, Union
from pandas import DataFrame, Series


class FileMerger:
    """Handles merging of Excel files with column mapping."""
    
    # Progress status states
    PROGRESS_STATES = {
        1: "📁 Ready to upload",
        2: "🔍 Checking files",
        3: "🔗 Mapping columns",
        4: "✨ Complete!"
    }
    
    def _load_and_validate_file(self, file) -> Tuple[Optional[pd.DataFrame], Dict]:
        """Load and validate a data file, returning the DataFrame and validation results."""
        validation = {
            'success': False,
            'errors': [],
            'warnings': [],
            'stats': {},
            'dtypes': {}
        }
        
        try:
            # Load file based on extension
            df = pd.read_csv(file) if file.name.lower().endswith('.csv') else pd.read_excel(file)
            
            # Calculate basic statistics efficiently
            validation['stats'] = {
                'rows': len(df),
                'columns': len(df.columns),
                'missing_data': int(df.isna().sum().sum()),
                'duplicate_rows': int(df.duplicated().sum()),
                'memory_usage': df.memory_usage(deep=True).sum() / (1024 * 1024)  # MB
            }
            
            # Validate column names and data
            dupes = df.columns[df.columns.duplicated()].tolist()
            empty_cols = [col for col in df.columns if df[col].isna().all()]
            
            if dupes:
                validation['errors'].append(f"Duplicate column names found: {', '.join(dupes)}")
            if empty_cols:
                validation['warnings'].append(f"Empty columns found: {', '.join(empty_cols)}")
                validation['empty_columns'] = empty_cols
            
            # Store data types
            validation['dtypes'] = df.dtypes.astype(str).to_dict()
            validation['success'] = len(validation['errors']) == 0
            
            return df, validation
            
        except Exception as e:
            validation['errors'].append(f"Failed to load file: {str(e)}")
            return None, validation

    def show_merger_interface(self) -> Optional[pd.DataFrame]:
        """Display the file merger interface."""
        self._show_header_and_help()
        
        # Initialize progress tracking
        if 'merger_step' not in st.session_state:
            st.session_state.merger_step = 1
            st.session_state.merger_files = None
            st.session_state.merger_dataframes = None
            st.session_state.merger_info = None
        
        # Show current progress
        self._show_progress_status()
        
        # Handle file upload and validation
        if st.session_state.merger_step == 1:
            if not self._handle_file_upload():
                return None
        
        # Handle file validation and preview
        if st.session_state.merger_step == 2:
            if not self._handle_file_validation():
                return None
        
        # Handle column mapping and merging
        if st.session_state.merger_step == 3:
            merged_data = self._handle_column_mapping()
            if merged_data is None:
                return None
            st.session_state.merged_data = merged_data
        
        # Show final results
        if st.session_state.merger_step == 4:
            self._show_merge_results()
            return st.session_state.merged_data
            
        return None
    
    def _show_header_and_help(self):
        """Display the merger interface header and help section."""
        st.markdown("""
        # 📊 Easy File Merger
        
        ### Merge your Excel and CSV files in 4 simple steps:
        
        1. 📁 **Drop your files** - Upload 2 or more Excel/CSV files
        2. 🔍 **Quick check** - We'll validate your files automatically
        3. 🔗 **Match columns** - Review or adjust how columns are matched
        4. ⬇️ **Download** - Get your merged file
        
        Need help? Click the '❓ Help' section below.
        """)
        
        with st.expander("❓ Help & Tips"):
            st.markdown("""
            **Common Questions:**
            
            - **Which file should I upload first?**
                - Your first file becomes the template, so upload your most important file first
            
            - **What happens to duplicate data?**
                - Duplicates are automatically removed to keep your data clean
            
            - **What if column names don't match?**
                - We automatically detect similar column names
                - You can manually adjust any matches
                - New columns will be added if needed
            
            **Tips:**
            - Clean your files before uploading for best results
            - Check the preview after each file is merged
            - Use 'Review each column' for more control
            """)
            
    def _show_progress_status(self):
        """Display the current progress status."""
        current_step = st.session_state.merger_step
        
        # Show progress bar and status
        col1, col2 = st.columns([4, 1])
        with col1:
            st.progress(current_step/4)
            st.caption(f"Status: {self.PROGRESS_STATES[current_step]}")
        
        # Add go back button if not on first step
        with col2:
            if current_step > 1:
                # Create a unique key for each step to avoid conflicts
                if st.button("⬅️ Go Back", key=f"go_back_step_{current_step}"):
                    # First clear any stored data for the current step
                    if current_step == 4:
                        if 'merged_data' in st.session_state:
                            del st.session_state.merged_data
                    elif current_step == 3:
                        if 'temp_merged_data' in st.session_state:
                            del st.session_state.temp_merged_data
                    elif current_step == 2:
                        if 'merger_dataframes' in st.session_state:
                            del st.session_state.merger_dataframes
                        if 'merger_info' in st.session_state:
                            del st.session_state.merger_info
                    
                    # Go back one step
                    st.session_state.merger_step -= 1
                    st.rerun()
        
        st.markdown("---")
        
    def _handle_file_upload(self) -> bool:
        """Handle file upload process and primary file selection."""
        # File uploader
        uploaded_files = st.file_uploader(
            "Drop your Excel or CSV files here",
            type=['xlsx', 'xls', 'csv'],
            accept_multiple_files=True,
            help="📌 The first file you upload will be used as the main template"
        )
        
        if not uploaded_files:
            st.info("👆 Start by dropping two or more files above")
            return False
            
        if len(uploaded_files) < 2:
            st.warning("🎯 Almost there! Drop at least one more file to start merging")
            return False
        
        # Primary file selection
        st.markdown("## 📌 Select Primary File")
        st.info("The primary file will be used as the base structure. Other files will be mapped to match its columns.")
        
        primary_file_index = st.selectbox(
            "Choose your primary file:",
            options=range(len(uploaded_files)),
            format_func=lambda x: f"File {x+1}: {uploaded_files[x].name}",
            help="Select the file that has your preferred column structure"
        )
        
        # Reorder files to put primary first
        if primary_file_index != 0:
            uploaded_files = [uploaded_files[primary_file_index]] + \
                           [f for i, f in enumerate(uploaded_files) if i != primary_file_index]
        
        st.session_state.merger_files = uploaded_files
        
        # Add confirmation button to proceed
        st.markdown("---")
        col1, col2, col3 = st.columns([2,2,1])
        with col2:
            if st.button("✅ Confirm and Continue", key="confirm_upload", type="primary"):
                st.session_state.merger_step = 2
                return True
            
        return False
        
    def _handle_file_validation(self) -> bool:
        """Validate uploaded files and show previews."""
        st.markdown("## 🔍 Step 2: File Validation")
        
        with st.spinner("🔄 Loading and validating files..."):
            dataframes = []
            file_info = []
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, file in enumerate(st.session_state.merger_files):
                status_text.text(f"Processing file {i+1} of {len(st.session_state.merger_files)}: {file.name}")
                progress_bar.progress((i + 1) / len(st.session_state.merger_files))
                
                df, validation = self._load_and_validate_file(file)
                
                if not validation['success']:
                    st.error(f"❌ Error loading {file.name}")
                    for error in validation['errors']:
                        st.error(f"• {error}")
                    return False
                
                dataframes.append(df)
                file_info.append({
                    'name': file.name,
                    'df': df,
                    'validation': validation
                })
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
        
        # Store data for next step
        st.session_state.merger_dataframes = dataframes
        st.session_state.merger_info = file_info
        
        # Show summary and previews
        self._show_file_summaries(file_info)
        self._show_file_previews(file_info)
        
        # Add confirmation button to proceed
        st.markdown("---")
        col1, col2, col3 = st.columns([2,2,1])
        with col2:
            if st.button("✅ Proceed to Mapping", key="confirm_validation", type="primary"):
                st.session_state.merger_step = 3
                return True
                
        return False
        
    def _show_file_summaries(self, file_info):
        """Display summary information for all files."""
        summary_data = [{
            "File": f"📄 {info['name'][:30]}{'...' if len(info['name']) > 30 else ''}",
            "Rows": f"{info['validation']['stats']['rows']:,}",
            "Columns": info['validation']['stats']['columns'],
            "Status": "✅ Ready" if info['validation']['success'] else "❌ Error"
        } for info in file_info]
        
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
        
    def _show_file_previews(self, file_info):
        """Show file previews in tabs."""
        st.markdown("### 👀 File Previews")
        tabs = st.tabs([f"File {i+1}: {info['name'][:20]}" for i, info in enumerate(file_info)])
        
        for i, (tab, info) in enumerate(zip(tabs, file_info)):
            with tab:
                if i == 0:
                    st.info("🎯 **Primary file** - Other files will be merged into this structure")
                st.dataframe(info['df'].head(10), use_container_width=True)
                
    def _handle_column_mapping(self) -> Optional[pd.DataFrame]:
        """Handle column mapping and merging process."""
        st.markdown("## 🔗 Step 3: Column Mapping")
        
        dataframes = st.session_state.merger_dataframes
        file_info = st.session_state.merger_info
        
        primary_df = dataframes[0]
        merged_data = primary_df.copy()
        
        # Process each secondary file
        for file_idx, secondary_df in enumerate(dataframes[1:], 1):
            with st.expander(f"🔧 Map columns for File {file_idx + 1}: {file_info[file_idx]['name']}", expanded=True):
                if not self._process_file_mapping(file_idx, merged_data, secondary_df, file_info):
                    return None
                merged_data = st.session_state.temp_merged_data
        
        # Add confirmation to complete the merge
        st.markdown("---")
        col1, col2, col3 = st.columns([2,2,1])
        with col2:
            if st.button("✅ Complete Merge", key="confirm_merge", type="primary"):
                st.session_state.merger_step = 4
                return merged_data
                
        return None
        
    def _process_file_mapping(self, file_idx: int, merged_data: pd.DataFrame, secondary_df: pd.DataFrame, file_info: List[Dict]) -> bool:
        """Process mapping for a single file."""
        st.markdown(f"**Merging:** {file_info[file_idx]['name']} → {file_info[0]['name']}")
        
        # Generate and display mappings
        mappings = self._generate_smart_mappings(merged_data, secondary_df)
        
        # Show automatic mapping statistics
        auto_mapped = len([m for m in mappings.values() if m is not None])
        new_columns = len(mappings) - auto_mapped
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🎯 Auto-mapped", auto_mapped)
        with col2:
            st.metric("🆕 New columns", new_columns)
        with col3:
            st.metric("📊 Total columns", len(mappings))
        
        st.markdown("### 🔍 Review and Edit Column Mappings")
        st.info("Review the automatic mappings below. You can change any mapping by selecting a different column from the dropdown.")
        
        # Create an interactive mapping table
        for sec_col in secondary_df.columns:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.markdown(f"**From:** `{sec_col}`")
                    # Show sample values from secondary file
                    sample = secondary_df[sec_col].dropna().head(2).tolist()
                    if sample:
                        st.caption(f"Sample: {', '.join(str(x)[:30] for x in sample)}")
                
                with col2:
                    # Dropdown to select mapping
                    options = ["➕ Create as new column"] + list(merged_data.columns)
                    # Find default index safely
                    default_idx = 0  # Default to "Create as new column"
                    mapped_col = mappings.get(sec_col)
                    if isinstance(mapped_col, str) and mapped_col in options:
                        default_idx = options.index(mapped_col)
                    
                    selected = st.selectbox(
                        "Map to:",
                        options,
                        index=default_idx,
                        key=f"mapping_select_{file_idx}_{sec_col}",
                        label_visibility="collapsed"
                    )
                    
                    # Update mapping based on selection
                    if selected == "➕ Create as new column":
                        mappings[sec_col] = None
                    else:
                        mappings[sec_col] = selected
                
                with col3:
                    if mappings[sec_col] is None:
                        st.markdown("🆕 New")
                    else:
                        # Show preview of matched column
                        matched_sample = merged_data[mappings[sec_col]].dropna().head(1).tolist()
                        if matched_sample:
                            st.caption(f"Match: {str(matched_sample[0])[:30]}")
                
                st.divider()
        
        # Apply mappings and merge
        try:
            st.session_state.temp_merged_data = self._apply_mappings_and_merge(merged_data, secondary_df, mappings)
            st.success(f"✅ Successfully mapped and merged File {file_idx + 1}")
            
            # Show preview of merged data
            with st.expander("👀 Preview Merged Data", expanded=False):
                st.dataframe(st.session_state.temp_merged_data.head(10), use_container_width=True)
                st.caption(f"Current merged data: {len(st.session_state.temp_merged_data)} rows, {len(st.session_state.temp_merged_data.columns)} columns")
            
            # Add navigation buttons
            st.markdown("---")
            col1, col2, col3 = st.columns([2,2,1])
            
            with col1:
                if file_idx > 1:  # Not the first secondary file
                    if st.button("⬅️ Previous File", key=f"prev_{file_idx}"):
                        st.rerun()
            
            with col2:
                if file_idx == len(st.session_state.merger_dataframes) - 2:  # If this is the last file
                    if st.button("✅ Complete Merge", key=f"complete_merge_{file_idx}", type="primary"):
                        # Store the final merged data
                        st.session_state.merged_data = st.session_state.temp_merged_data
                        st.session_state.merger_step = 4
                        st.rerun()
                else:
                    if st.button("➡️ Next File", key=f"next_{file_idx}", type="primary"):
                        st.rerun()
            
            with col3:
                if st.button("🔄 Restart", key=f"restart_{file_idx}"):
                    st.session_state.merger_step = 1
                    st.rerun()
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error merging File {file_idx + 1}: {str(e)}")
            import traceback
            st.error(f"Full error: {traceback.format_exc()}")
            return False
            
    def _show_merge_results(self):
        """Display the final merge results."""
        st.markdown("## 🎉 Step 4: Merge Complete!")
        
        merged_data = st.session_state.merged_data
        original_files = st.session_state.merger_files
        original_dfs = st.session_state.merger_dataframes
        
        # Calculate comprehensive statistics
        total_original_rows = sum(len(df) for df in original_dfs)
        duplicates_removed = total_original_rows - len(merged_data)
        data_loss_percentage = (duplicates_removed / total_original_rows * 100) if total_original_rows > 0 else 0
        
        # Show comprehensive statistics
        st.markdown("### 📊 Merge Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📄 Files merged", len(original_files))
        with col2:
            st.metric("📊 Total rows", f"{len(merged_data):,}")
        with col3:
            st.metric("📋 Total columns", len(merged_data.columns))
        with col4:
            st.metric("🗑️ Duplicates removed", f"{duplicates_removed:,}")
        
        # Data quality indicators
        st.markdown("### 🔍 Data Quality Check")
        col1, col2, col3 = st.columns(3)
        with col1:
            if data_loss_percentage < 5:
                st.success(f"✅ Low data loss: {data_loss_percentage:.1f}%")
            elif data_loss_percentage < 15:
                st.warning(f"⚠️ Moderate data loss: {data_loss_percentage:.1f}%")
            else:
                st.error(f"❌ High data loss: {data_loss_percentage:.1f}%")
        
        with col2:
            null_percentage = (merged_data.isnull().sum().sum() / (len(merged_data) * len(merged_data.columns)) * 100)
            if null_percentage < 10:
                st.success(f"✅ Low missing data: {null_percentage:.1f}%")
            elif null_percentage < 25:
                st.warning(f"⚠️ Moderate missing data: {null_percentage:.1f}%")
            else:
                st.error(f"❌ High missing data: {null_percentage:.1f}%")
        
        with col3:
            st.info(f"📈 Data completeness: {100 - null_percentage:.1f}%")
        
        # Show detailed file breakdown
        st.markdown("### 📋 File Breakdown")
        breakdown_data = []
        for i, (file, df) in enumerate(zip(original_files, original_dfs)):
            breakdown_data.append({
                "File": file.name,
                "Rows": len(df),
                "Columns": len(df.columns),
                "Status": "✅ Merged" if i < len(original_dfs) else "❌ Failed"
            })
        
        st.dataframe(pd.DataFrame(breakdown_data), use_container_width=True)
        
        # Show preview
        st.markdown("### 👀 Preview Merged Data")
        st.dataframe(merged_data.head(20), use_container_width=True)
        
        # Success message and next steps
        if data_loss_percentage < 15:
            st.success("🎊 **Merge completed successfully!** Your data has been merged with minimal loss.")
        else:
            st.warning("⚠️ **Merge completed with data loss.** Please review the statistics above.")
        
        # Action buttons
        st.markdown("### 🚀 Next Steps")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.download_button(
                "⬇️ Download CSV",
                data=merged_data.to_csv(index=False),
                file_name="merged_data.csv",
                mime="text/csv",
                key="download_csv"
            )
        
        with col2:
            st.download_button(
                "⬇️ Download Excel",
                data=self._dataframe_to_excel_bytes(merged_data),
                file_name="merged_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_excel"
            )
        
        with col3:
            if st.button("🔧 Transform Data", key="transform_data", type="primary"):
                # Store merged data for transformation
                st.session_state['data'] = merged_data
                st.session_state['single_steps']['upload'] = True
                st.success("✅ Data ready for transformation! Switch to the Single File workflow.")
        
        with col4:
            if st.button("🔄 New Merge", key="new_merge"):
                # Reset all session state variables
                st.session_state.merger_step = 1
                st.session_state.merger_files = None
                st.session_state.merger_dataframes = None
                st.session_state.merger_info = None
                st.session_state.merged_data = None
                st.rerun()
    
    def _dataframe_to_excel_bytes(self, df: pd.DataFrame) -> bytes:
        """Convert DataFrame to Excel bytes for download."""
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Merged Data')
        return output.getvalue()

    def _generate_smart_mappings(self, primary_df: pd.DataFrame, secondary_df: pd.DataFrame) -> Dict[str, Optional[str]]:
        """Generate smart column mappings between primary and secondary dataframes with AST-specific logic."""
        mappings = {}
        used_primary_cols = set()  # Track used primary columns
        
        # Process columns by similarity
        similarity_scores = []
        
        # Calculate all similarity scores first
        for sec_col in secondary_df.columns:
            for pri_col in primary_df.columns:
                # Use the sophisticated similarity analysis
                similarity_report = self.analyze_column_similarity(
                    pri_col, primary_df[pri_col], 
                    sec_col, secondary_df[sec_col]
                )
                
                score = similarity_report['score']
                
                # Additional AST-specific matching logic
                if score < 0.9:  # Only apply if we don't have a perfect match
                    ast_score = self._check_ast_patterns(pri_col, sec_col)
                    if ast_score > score:
                        score = ast_score
                        
                if score > 0.5:  # Only consider scores above threshold
                    similarity_scores.append((score, sec_col, pri_col))
        
        # Sort by score descending to process best matches first
        similarity_scores.sort(reverse=True)
        
        # Assign mappings in order of best matches
        for score, sec_col, pri_col in similarity_scores:
            if sec_col not in mappings and pri_col not in used_primary_cols:
                mappings[sec_col] = pri_col
                used_primary_cols.add(pri_col)
        
        # Handle any remaining unmapped columns
        for sec_col in secondary_df.columns:
            if sec_col not in mappings:
                mappings[sec_col] = None  # Will create as new column
                
        return mappings

    def _check_ast_patterns(self, col1: str, col2: str) -> float:
        """Check for AST-specific column patterns like AMC_ND20 → INT_AMC."""
        import re
        
        def extract_antibiotic_code(col_name):
            """Extract antibiotic codes from column names."""
            col_clean = col_name.upper().strip()
            
            # Common AST patterns
            patterns = [
                r'([A-Z]{2,4})_ND\d+',  # AMC_ND20 → AMC
                r'([A-Z]{2,4})_MIC',    # AMC_MIC → AMC
                r'([A-Z]{2,4})_DISK',   # AMC_DISK → AMC
                r'INT_([A-Z]{2,4})',    # INT_AMC → AMC
                r'SIR_([A-Z]{2,4})',    # SIR_AMC → AMC
                r'([A-Z]{2,4})_INT',    # AMC_INT → AMC
                r'([A-Z]{2,4})_SIR',    # AMC_SIR → AMC
                r'^([A-Z]{2,4})$',      # Direct antibiotic codes
                r'([A-Z]{2,4})_\d+',    # AMC_30 → AMC (disk concentrations)
            ]
            
            for pattern in patterns:
                match = re.search(pattern, col_clean)
                if match:
                    return match.group(1)
            
            return None
        
        # Extract antibiotic codes from both columns
        code1 = extract_antibiotic_code(col1)
        code2 = extract_antibiotic_code(col2)
        
        if code1 and code2:
            if code1 == code2:
                return 0.95  # High confidence match for same antibiotic
            
            # Check for common antibiotic synonyms
            synonyms = {
                'AMC': ['AUG', 'AMOXICLAV'],
                'AMP': ['AMPICILLIN'],
                'CIP': ['CIPRO'],
                'CTX': ['CEFOTAXIME'],
                'CAZ': ['CEFTAZIDIME'],
                'GEN': ['GENTAMICIN'],
                'TOB': ['TOBRAMYCIN'],
                'TET': ['TETRACYCLINE'],
                'CHL': ['CHLORAMPHENICOL'],
                'SXT': ['COTRIMOXAZOLE', 'TMP'],
            }
            
            for main_code, alt_codes in synonyms.items():
                if ((code1 == main_code and code2 in alt_codes) or
                    (code2 == main_code and code1 in alt_codes) or
                    (code1 in alt_codes and code2 in alt_codes)):
                    return 0.9
        
        return 0.0

    def _show_mapping_summary(self, mappings: Dict[str, Optional[str]], file_idx: int):
        """Show a concise summary of automatic column mappings."""
        st.markdown("#### 📋 Column Mapping Summary")
        
        # Create mapping summary in a single pass
        summary_data = [{
            "From": sec_col,
            "To": pri_col if pri_col else "New column",
            "Status": "✅ Will merge" if pri_col else "➕ Will add"
        } for sec_col, pri_col in mappings.items()]
        
        # Show statistics
        merged_count = sum(1 for item in summary_data if item["Status"].startswith("✅"))
        new_count = len(summary_data) - merged_count
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🔗 Columns to merge", merged_count)
        with col2:
            st.metric("➕ New columns", new_count)
        
        # Show mapping table
        st.dataframe(
            pd.DataFrame(summary_data),
            use_container_width=True,
            hide_index=True
        )

    def _show_detailed_mapping_interface(self, primary_df: pd.DataFrame, secondary_df: pd.DataFrame, mappings: Dict[str, Optional[str]], file_idx: int):
        """Show an enhanced column mapping interface."""
        st.markdown("""
        #### 🔍 Review Column Mappings
        Adjust how columns are matched between your files. For each column, you can:
        - Keep the automatic match
        - Choose a different column to merge with
        - Create as a new column
        """)
        
        for sec_col in secondary_df.columns:
            auto_mapped = mappings.get(sec_col)
            
            with st.container():
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown(f"**Secondary:** `{sec_col}`")
                    # Show sample data
                    sample_data = secondary_df[sec_col].dropna().head(3).tolist()
                    if sample_data:
                        st.caption("Sample values:")
                        for val in sample_data[:3]:
                            st.caption(f"• {str(val)[:50]}")
                
                with col2:
                    # Column selection
                    options = ["➕ Create as new column"] + list(primary_df.columns)
                    default_idx = 0
                    
                    if auto_mapped and auto_mapped in options:
                        default_idx = options.index(auto_mapped)
                    
                    selected = st.selectbox(
                        f"Map to:",
                        options,
                        index=default_idx,
                        key=f"mapping_{file_idx}_{sec_col}",
                        label_visibility="collapsed"
                    )
                    
                    # Update mapping
                    if selected == "➕ Create as new column":
                        mappings[sec_col] = None
                    else:
                        mappings[sec_col] = selected
                
                st.divider()

    def _apply_mappings_and_merge(self, primary_df: pd.DataFrame, secondary_df: pd.DataFrame, mappings: Dict[str, Optional[str]]) -> pd.DataFrame:
        """Apply column mappings and merge dataframes."""
        try:
            # Create working copies with improved data type handling
            primary_work = self._prepare_dataframe_for_merge(primary_df)
            secondary_work = self._prepare_dataframe_for_merge(secondary_df)
            
            # Initialize tracking for column names
            final_columns = []
            used_names = set()
            rename_map = {}

            # First, handle explicitly mapped columns
            for sec_col, pri_col in mappings.items():
                if pri_col:  # Map to existing column
                    rename_map[sec_col] = pri_col
                    if pri_col not in used_names:
                        final_columns.append(pri_col)
                        used_names.add(pri_col)

            # Then handle unmapped columns (new columns)
            for sec_col in secondary_df.columns:
                if sec_col not in rename_map:  # This is a new column
                    new_name = sec_col
                    # Handle potential name conflicts
                    counter = 1
                    while new_name in used_names:
                        new_name = f"{sec_col}_{counter}"
                        counter += 1
                    rename_map[sec_col] = new_name
                    final_columns.append(new_name)
                    used_names.add(new_name)

            # Rename secondary dataframe columns
            secondary_work = secondary_work.rename(columns=rename_map)

            # Add any missing columns from primary_df that weren't in mappings
            for col in primary_work.columns:
                if col not in used_names:
                    final_columns.append(col)
                    used_names.add(col)

            # Ensure all columns exist in both dataframes with consistent data types
            # Use bulk operations to avoid DataFrame fragmentation warnings
            missing_primary_cols = [col for col in final_columns if col not in primary_work.columns]
            missing_secondary_cols = [col for col in final_columns if col not in secondary_work.columns]
            
            # Add missing columns in bulk
            if missing_primary_cols:
                primary_work = pd.concat([
                    primary_work,
                    pd.DataFrame({col: [None] * len(primary_work) for col in missing_primary_cols}, dtype='object')
                ], axis=1)
            
            if missing_secondary_cols:
                secondary_work = pd.concat([
                    secondary_work,
                    pd.DataFrame({col: [None] * len(secondary_work) for col in missing_secondary_cols}, dtype='object')
                ], axis=1)
            
            # Harmonize data types for all columns at once
            for col in final_columns:
                if col in primary_work.columns and col in secondary_work.columns:
                    self._harmonize_column_types(primary_work, secondary_work, col)

            # Reorder columns safely
            primary_work = primary_work.reindex(columns=final_columns)
            secondary_work = secondary_work.reindex(columns=final_columns)

            # Perform the merge using concat with improved data type handling
            # Ensure consistent data types before concatenation
            for col in final_columns:
                if col in primary_work.columns and col in secondary_work.columns:
                    # Convert both columns to the same type
                    primary_col = primary_work[col]
                    secondary_col = secondary_work[col]
                    
                    # Handle mixed data types
                    if primary_col.dtype != secondary_col.dtype:
                        # Convert both to object type to avoid conflicts
                        primary_work[col] = primary_col.astype(str)
                        secondary_work[col] = secondary_col.astype(str)
            
            # Filter out completely empty dataframes before concat
            primary_work_filtered = primary_work.dropna(how='all')
            secondary_work_filtered = secondary_work.dropna(how='all')
            
            if len(primary_work_filtered) > 0 and len(secondary_work_filtered) > 0:
                merged = pd.concat(
                    [primary_work_filtered, secondary_work_filtered],
                    axis=0,
                    ignore_index=True,
                    sort=False
                )
            elif len(primary_work_filtered) > 0:
                merged = primary_work_filtered.copy()
            elif len(secondary_work_filtered) > 0:
                merged = secondary_work_filtered.copy()
            else:
                # Both are empty, return empty dataframe with correct columns
                merged = pd.DataFrame(columns=final_columns)

            # Remove duplicates if any
            merged = merged.drop_duplicates().reset_index(drop=True)

            return merged

        except Exception as e:
            # Add more context to the error message
            error_msg = f"Error during merge: {str(e)}"
            st.error(error_msg)
            st.error(f"Primary columns: {list(primary_df.columns)}")
            st.error(f"Secondary columns: {list(secondary_df.columns)}")
            
            # Log the error for debugging
            import traceback
            st.error(f"Full error traceback: {traceback.format_exc()}")
            
            # Try to provide a partial merge result
            try:
                st.warning("Attempting to create a partial merge result...")
                # Create a simple merge with just the primary dataframe
                partial_result = primary_df.copy()
                st.success("Partial merge completed with primary dataframe only.")
                return partial_result
            except Exception as partial_error:
                st.error(f"Could not create partial merge: {str(partial_error)}")
                raise Exception(error_msg) from e

    def analyze_column_similarity(self, col1_name: str, col1_data: pd.Series, col2_name: str, col2_data: pd.Series) -> Dict:
        """
        Analyze similarity between two columns based on name similarity and data patterns.
        Returns a comprehensive similarity report.
        """
        import re
        from difflib import SequenceMatcher
        
        report = {
            'name_similarity': 0.0,
            'data_similarity': 0.0,
            'score': 0.0,
            'match_details': []
        }
        
        def clean_column_name(name):
            """Clean and standardize column names."""
            if not isinstance(name, str):
                name = str(name)
            
            # Clean whitespace and convert to lowercase
            name = name.strip().lower()
            name = re.sub(r'\s+', ' ', name)
            
            # Convert special characters to underscores
            name = re.sub(r'[-_\s\./\\]+', '_', name)
            name = re.sub(r'[^a-z0-9_]', '', name)
            
            # Remove common prefixes/suffixes
            name = re.sub(r'^(id|code|dt|date|num|number|col|column|field|value)_', '', name)
            name = re.sub(r'_(id|code|dt|date|num|number|col|column|field|value)$', '', name)
            
            # Final cleanup
            name = name.strip('_')
            name = re.sub(r'_+', '_', name)
            
            return name
            
        def get_name_variations(name):
            """Get common variations of column names for matching."""
            variations = {name}
            
            # Define common patterns for lab data
            patterns = {
                r'(\w+)_nd(\d+)': r'\1',          # AMC_ND20 -> AMC
                r'(\w+)_mic': r'\1',              # AMC_MIC -> AMC
                r'(\w+)_disk': r'\1',             # AMC_DISK -> AMC
                r'int_(\w+)': r'\1',              # INT_AMC -> AMC
                r'sir_(\w+)': r'\1',              # SIR_AMC -> AMC
                r'(\w+)_int': r'\1',              # AMC_INT -> AMC
                r'(\w+)_sir': r'\1',              # AMC_SIR -> AMC
                r'(\w+)_\d+': r'\1',              # AMC_30 -> AMC
            }
            
            # Apply patterns
            for pattern, replacement in patterns.items():
                if re.search(pattern, name):
                    variations.add(re.sub(pattern, replacement, name))
            
            # Handle separators
            words = re.split(r'[_\s\-\.]+', name)
            variations.update({'_'.join(words), ' '.join(words), '-'.join(words)})
            
            # Handle singular/plural
            variations.add(name + ('s' if not name.endswith('s') else ''))
            variations.add(name[:-1] if name.endswith('s') else name)
            
            return variations
        
        # Clean column names and get variations
        name1 = clean_column_name(col1_name)
        name2 = clean_column_name(col2_name)
        variations1 = get_name_variations(name1)
        variations2 = get_name_variations(name2)
        
        # Calculate similarity scores
        exact_match = name1 == name2
        contains = name1 in name2 or name2 in name1
        sequence_similarity = SequenceMatcher(None, name1, name2).ratio()
        
        # Check for variation matches
        variation_match = any(
            SequenceMatcher(None, var1, var2).ratio() > 0.8 
            for var1 in variations1 
            for var2 in variations2
        )
        
        # Calculate final score
        name_scores = [
            (1.0 if exact_match else 0.0, "Exact match"),
            (0.95 if variation_match else 0.0, "Variation match"),
            (0.85 if contains else 0.0, "Containment match"),
            (sequence_similarity if sequence_similarity > 0.5 else 0.0, "Sequence similarity")
        ]
        
        best_score, best_reason = max(name_scores, key=lambda x: x[0])
        
        # Bonus scoring
        words1 = set(name1.split('_'))
        words2 = set(name2.split('_'))
        if words1.intersection(words2) and len(words1) == 1 and len(words2) == 1:
            best_score = min(1.0, best_score + 0.1)
        
        if (name1.startswith(name2) or name1.endswith(name2) or 
            name2.startswith(name1) or name2.endswith(name1)):
            best_score = min(1.0, best_score + 0.05)
        
        # Calculate data similarity
        data_similarity = self._calculate_data_similarity(col1_data, col2_data)
        
        # Set final scores and details
        report['name_similarity'] = best_score
        report['data_similarity'] = data_similarity
        report['score'] = max(best_score, data_similarity * 0.7)  # Weight data similarity less than name similarity
        
        # Add match details (only once)
        if report['score'] > 0:
            if exact_match:
                report['match_details'].append("Exact name match")
            elif variation_match:
                report['match_details'].append("Common variation match")
            elif contains:
                report['match_details'].append("Name containment match")
            elif sequence_similarity > 0.5:
                report['match_details'].append(f"Similar names ({sequence_similarity:.0%} match)")
            
            if data_similarity > 0.5:
                report['match_details'].append(f"Similar data patterns ({data_similarity:.0%} match)")
        else:
            report['match_details'].append(f"Partial match (name: {sequence_similarity:.2f}, data: {data_similarity:.2f})")
        
        return report
    
    def _calculate_data_similarity(self, col1_data: pd.Series, col2_data: pd.Series) -> float:
        """Calculate similarity based on data patterns and values."""
        try:
            # Handle empty or all-null columns
            if col1_data.isna().all() or col2_data.isna().all():
                return 0.0
            
            # Get non-null samples
            sample1 = col1_data.dropna().head(100)
            sample2 = col2_data.dropna().head(100)
            
            if len(sample1) == 0 or len(sample2) == 0:
                return 0.0
            
            # Check data type compatibility
            type1 = col1_data.dtype
            type2 = col2_data.dtype
            
            # If both are numeric, check value ranges
            if pd.api.types.is_numeric_dtype(type1) and pd.api.types.is_numeric_dtype(type2):
                range1 = (sample1.min(), sample1.max())
                range2 = (sample2.min(), sample2.max())
                
                # Calculate range overlap
                overlap = max(0, min(range1[1], range2[1]) - max(range1[0], range2[0]))
                total_range = max(range1[1], range2[1]) - min(range1[0], range2[0])
                
                if total_range > 0:
                    return overlap / total_range
                else:
                    return 1.0 if range1 == range2 else 0.0
            
            # If both are categorical, check value overlap
            elif type1 == 'object' and type2 == 'object':
                values1 = set(sample1.astype(str))
                values2 = set(sample2.astype(str))
                
                if len(values1) == 0 or len(values2) == 0:
                    return 0.0
                
                intersection = len(values1.intersection(values2))
                union = len(values1.union(values2))
                
                return intersection / union if union > 0 else 0.0
            
            # Mixed types - check if values can be converted to same type
            else:
                try:
                    # Try to convert both to numeric
                    num1 = pd.to_numeric(sample1, errors='coerce')
                    num2 = pd.to_numeric(sample2, errors='coerce')
                    
                    if not num1.isna().all() and not num2.isna().all():
                        # Both can be converted to numeric
                        return 0.7  # Moderate similarity
                except:
                    pass
                
                try:
                    # Try to convert both to datetime
                    pd.to_datetime(sample1, errors='coerce')
                    pd.to_datetime(sample2, errors='coerce')
                    return 0.6  # Moderate similarity for date-like data
                except:
                    pass
                
                return 0.3  # Low similarity for mixed types
            
        except Exception:
            return 0.0
    
    def _prepare_dataframe_for_merge(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare a dataframe for merging by ensuring consistent data types."""
        df_copy = df.copy()
        
        for col in df_copy.columns:
            try:
                # Handle datetime columns
                if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
                    df_copy[col] = df_copy[col].astype(str)
                # Handle mixed-type object columns
                elif df_copy[col].dtype == 'object':
                    # Check for mixed types
                    sample_values = df_copy[col].dropna().head(10)
                    if len(sample_values) > 0:
                        has_numeric = any(pd.to_numeric(sample_values, errors='coerce').notna())
                        has_string = any(isinstance(x, str) for x in sample_values if pd.notna(x))
                        
                        if has_numeric and has_string:
                            # Mixed types - convert all to string
                            df_copy[col] = df_copy[col].astype(str)
                        elif has_numeric:
                            # All numeric - convert to numeric
                            df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce')
                        else:
                            # All string - ensure consistent string type
                            df_copy[col] = df_copy[col].astype(str)
                    else:
                        # Empty column - keep as object
                        df_copy[col] = df_copy[col].astype(str)
                # Handle numeric columns
                elif pd.api.types.is_numeric_dtype(df_copy[col]):
                    # Ensure numeric columns are properly typed
                    df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce')
            except Exception:
                # If any conversion fails, convert to string as fallback
                df_copy[col] = df_copy[col].astype(str)
        
        return df_copy
    
    def _harmonize_column_types(self, df1: pd.DataFrame, df2: pd.DataFrame, col: str):
        """Harmonize data types between two dataframes for a specific column."""
        try:
            col1 = df1[col]
            col2 = df2[col]
            
            # If both columns have the same type, no need to change
            if col1.dtype == col2.dtype:
                return
            
            # If one is numeric and the other is not, convert both to string
            if (pd.api.types.is_numeric_dtype(col1) and not pd.api.types.is_numeric_dtype(col2)) or \
               (pd.api.types.is_numeric_dtype(col2) and not pd.api.types.is_numeric_dtype(col1)):
                df1[col] = col1.astype(str)
                df2[col] = col2.astype(str)
            # If both are numeric but different types, convert to the more general type
            elif pd.api.types.is_numeric_dtype(col1) and pd.api.types.is_numeric_dtype(col2):
                if 'float' in str(col1.dtype) or 'float' in str(col2.dtype):
                    df1[col] = col1.astype(float)
                    df2[col] = col2.astype(float)
                else:
                    df1[col] = col1.astype(int)
                    df2[col] = col2.astype(int)
            # If both are object types, ensure they're both strings
            else:
                df1[col] = col1.astype(str)
                df2[col] = col2.astype(str)
        except Exception:
            # If harmonization fails, convert both to string
            df1[col] = df1[col].astype(str)
            df2[col] = df2[col].astype(str)
