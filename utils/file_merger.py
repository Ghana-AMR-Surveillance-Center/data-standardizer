"""
File Merger Module
Handles intelligent merging of multiple Excel/CSV files with advanced column mapping.

This module provides comprehensive file merging capabilities including:
- Multi-file upload and validation
- Intelligent column mapping with fuzzy matching
- Data type harmonization and conversion
- Duplicate detection and removal
- Progress tracking and user feedback
- Error handling and recovery

Key Features:
- One-file-at-a-time processing workflow
- Automatic column mapping suggestions
- Manual mapping override capabilities
- Data quality validation
- Memory-efficient processing
- Professional user interface

Author: GLASS Data Standardizer Team
Version: 2.0.0
"""
from __future__ import annotations

import streamlit as st
import pandas as pd
from typing import Any, Dict, List, Tuple, Optional
from pandas import DataFrame, Series


class FileMerger:
    """
    Handles intelligent merging of Excel/CSV files with advanced column mapping.
    
    This class provides a comprehensive file merging solution that processes multiple
    files sequentially, allowing users to map columns for each file individually
    before merging them into a unified dataset.
    
    Attributes:
        PROGRESS_STATES (dict): Mapping of step numbers to progress descriptions
        similarity_cache (dict): Cache for column similarity calculations
        max_cache_size (int): Maximum number of cached similarity calculations
        
    Methods:
        show_merger_interface(): Main interface for file merging workflow
        _load_and_validate_file(): Load and validate individual files
        _handle_column_mapping(): Process column mapping for each file
        _generate_smart_mappings(): Generate intelligent column mappings
        _apply_mappings_and_merge(): Apply mappings and merge data
        clear_cache(): Clear similarity calculation cache
        
    Example:
        >>> merger = FileMerger()
        >>> merged_data = merger.show_merger_interface()
        >>> if merged_data is not None:
        ...     print(f"Merged {len(merged_data)} rows successfully")
    """
    
    # Progress status states
    PROGRESS_STATES = {
        1: "📁 Ready to upload",
        2: "🔍 Checking files",
        3: "🔗 Mapping columns",
        4: "✨ Complete!"
    }
    
    def __init__(self):
        # Cache for similarity calculations to avoid recomputation
        self._similarity_cache = {}
        self._column_variations_cache = {}
    
    def clear_cache(self):
        """Clear all caches to free memory."""
        self._similarity_cache.clear()
        self._column_variations_cache.clear()
    
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
            # Load file based on extension with proper error handling
            if file.name.lower().endswith('.csv'):
                df = pd.read_csv(file)
            else:
                # Try different Excel engines for better compatibility
                try:
                    df = pd.read_excel(file, engine='openpyxl')
                except Exception:
                    try:
                        df = pd.read_excel(file, engine='xlrd')
                    except Exception:
                        # Fallback to default engine
                        df = pd.read_excel(file)
            
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
        
        # Add cache management
        if st.button("🗑️ Clear Mapping Cache", help="Clear cached similarity calculations to free memory"):
            self.clear_cache()
            st.success("Mapping cache cleared!")
            st.rerun()
        
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
                # Reset merger state for new process
                if 'current_file_idx' in st.session_state:
                    del st.session_state.current_file_idx
                if 'merged_data' in st.session_state:
                    del st.session_state.merged_data
                if 'temp_merged_data' in st.session_state:
                    del st.session_state.temp_merged_data
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
        
        # Initialize current file index if not set
        if 'current_file_idx' not in st.session_state:
            st.session_state.current_file_idx = 1  # Start with first secondary file
            st.session_state.merged_data = dataframes[0].copy()  # Start with primary file
        
        current_file_idx = st.session_state.current_file_idx
        merged_data = st.session_state.merged_data
        
        # Show progress
        total_files = len(dataframes)
        st.progress(current_file_idx / total_files, text=f"Processing file {current_file_idx} of {total_files}")
        
        # Check if we've processed all files
        if current_file_idx >= len(dataframes):
            # All files processed, show completion options
            st.success("🎉 All files have been processed!")
            st.markdown("---")
            col1, col2, col3 = st.columns([2,2,1])
            with col2:
                if st.button("✅ Complete Merge", key="confirm_merge", type="primary"):
                    st.session_state.merger_step = 4
                    return merged_data
            return None
        
        # Process current file
        secondary_df = dataframes[current_file_idx]
        
        # Show current file info
        st.info(f"📄 **Current File:** {file_info[current_file_idx]['name']} ({file_info[current_file_idx]['validation']['stats']['rows']} rows, {file_info[current_file_idx]['validation']['stats']['columns']} columns)")
        
        # Show instructions
        st.markdown("### 📋 Instructions")
        st.markdown("""
        1. **Review the automatic column mappings** below
        2. **Adjust any mappings** if needed using the dropdown menus
        3. **Click 'Apply Mappings'** to merge this file with the previous data
        4. **Click 'Next File'** to continue or **'Complete Merge'** if this is the last file
        """)
        
        # Show file processing status
        st.markdown("### 📊 File Processing Status")
        processed_files = current_file_idx
        remaining_files = total_files - current_file_idx
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("✅ Processed", processed_files)
        with col2:
            st.metric("⏳ Remaining", remaining_files)
        with col3:
            st.metric("📁 Total", total_files)
        
        with st.expander(f"🔧 Map columns for File {current_file_idx + 1}: {file_info[current_file_idx]['name']}", expanded=True):
            if not self._process_file_mapping(current_file_idx, merged_data, secondary_df, file_info):
                return None
                
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
        
        # Validate mappings before applying
        duplicate_mappings = self._validate_mappings(mappings)
        if duplicate_mappings:
            st.error("🚨 **Cannot proceed with duplicate mappings. Please resolve the following conflicts:**")
            for primary_col, secondary_cols in duplicate_mappings.items():
                st.error(f"• Column '{primary_col}' is mapped to by: {', '.join(secondary_cols)}")
            return False
        
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
                        # Move to previous file
                        st.session_state.current_file_idx = file_idx - 1
                        st.rerun()
            
            with col2:
                if file_idx == len(st.session_state.merger_dataframes) - 1:  # If this is the last file
                    if st.button("✅ Complete Merge (Last File)", key=f"complete_merge_{file_idx}", type="primary"):
                        # Store the final merged data
                        st.session_state.merged_data = st.session_state.temp_merged_data
                        st.session_state.merger_step = 4
                        st.rerun()
                else:
                    if st.button(f"➡️ Next File ({file_idx + 1}/{len(st.session_state.merger_dataframes)})", key=f"next_{file_idx}", type="primary"):
                        # Move to next file
                        st.session_state.current_file_idx = file_idx + 1
                        st.rerun()
            
            with col3:
                if st.button("🔄 Restart", key=f"restart_{file_idx}"):
                    # Reset all merger state
                    st.session_state.merger_step = 1
                    if 'current_file_idx' in st.session_state:
                        del st.session_state.current_file_idx
                    if 'merged_data' in st.session_state:
                        del st.session_state.merged_data
                    if 'temp_merged_data' in st.session_state:
                        del st.session_state.temp_merged_data
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
        
        # Create progress bar for mapping process
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Pre-filter columns for better performance
        primary_cols = list(primary_df.columns)
        secondary_cols = list(secondary_df.columns)
        
        # Process columns by similarity with early termination
        similarity_scores = []
        total_comparisons = len(secondary_cols) * len(primary_cols)
        current_comparison = 0
        
        # Calculate similarity scores with caching and early termination
        for sec_col in secondary_cols:
            best_score = 0.0
            best_pri_col = None
            
            for pri_col in primary_cols:
                current_comparison += 1
                progress = current_comparison / total_comparisons
                progress_bar.progress(progress)
                status_text.text(f"Analyzing column similarity: {sec_col} vs {pri_col}")
                
                # Check cache first
                cache_key = f"{sec_col}|{pri_col}"
                if cache_key in self._similarity_cache:
                    score = self._similarity_cache[cache_key]
                else:
                    # Use optimized similarity analysis
                    similarity_report = self._analyze_column_similarity_optimized(
                        pri_col, primary_df[pri_col], 
                        sec_col, secondary_df[sec_col]
                    )
                    score = similarity_report['score']
                    self._similarity_cache[cache_key] = score
                
                # Additional AST-specific matching logic (cached)
                if score < 0.9:  # Only apply if we don't have a perfect match
                    ast_cache_key = f"ast|{pri_col}|{sec_col}"
                    if ast_cache_key in self._similarity_cache:
                        ast_score = self._similarity_cache[ast_cache_key]
                    else:
                        ast_score = self._check_ast_patterns(pri_col, sec_col)
                        self._similarity_cache[ast_cache_key] = ast_score
                    
                    if ast_score > score:
                        score = ast_score
                
                # Early termination for high-confidence matches
                if score > 0.95:
                    similarity_scores.append((score, sec_col, pri_col))
                    break  # Skip remaining comparisons for this secondary column
                elif score > best_score:
                    best_score = score
                    best_pri_col = pri_col
                
                # Early termination if we have a very good match
                if best_score > 0.9:
                    break
            
            # Add the best match for this secondary column
            if best_score > 0.5:  # Only consider scores above threshold
                similarity_scores.append((best_score, sec_col, best_pri_col))
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Sort by score descending to process best matches first
        similarity_scores.sort(reverse=True)
        
        # Assign mappings in order of best matches
        for score, sec_col, pri_col in similarity_scores:
            if sec_col not in mappings and pri_col not in used_primary_cols:
                mappings[sec_col] = pri_col
                used_primary_cols.add(pri_col)
        
        # Handle any remaining unmapped columns
        for sec_col in secondary_cols:
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
        summary_data = []
        duplicate_warnings = []
        
        # Track which primary columns are mapped to
        primary_mappings = {}
        
        for sec_col, pri_col in mappings.items():
            if pri_col:
                if pri_col in primary_mappings:
                    # Duplicate mapping detected
                    duplicate_warnings.append(f"⚠️ Multiple columns mapping to '{pri_col}': {primary_mappings[pri_col]} and {sec_col}")
                    summary_data.append({
                        "From": sec_col,
                        "To": pri_col,
                        "Status": "❌ Duplicate mapping"
                    })
                else:
                    primary_mappings[pri_col] = sec_col
                    summary_data.append({
                        "From": sec_col,
                        "To": pri_col,
                        "Status": "✅ Will merge"
                    })
            else:
                summary_data.append({
                    "From": sec_col,
                    "To": "New column",
                    "Status": "➕ Will add"
                })
        
        # Show duplicate warnings if any
        if duplicate_warnings:
            st.error("🚨 **Duplicate Mappings Detected:**")
            for warning in duplicate_warnings:
                st.error(warning)
            st.error("Please resolve duplicate mappings before proceeding.")
        
        # Show statistics
        merged_count = sum(1 for item in summary_data if item["Status"].startswith("✅"))
        new_count = sum(1 for item in summary_data if item["Status"].startswith("➕"))
        duplicate_count = sum(1 for item in summary_data if item["Status"].startswith("❌"))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔗 Columns to merge", merged_count)
        with col2:
            st.metric("➕ New columns", new_count)
        with col3:
            st.metric("❌ Duplicates", duplicate_count)
        
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
                    # Column selection with dynamic options
                    # Get already mapped columns (excluding current column)
                    already_mapped_cols = {
                        mappings.get(other_sec_col) 
                        for other_sec_col in secondary_df.columns 
                        if other_sec_col != sec_col and mappings.get(other_sec_col) is not None
                    }
                    
                    # Create options with availability indicators
                    options = ["➕ Create as new column"]
                    for col in primary_df.columns:
                        if col in already_mapped_cols:
                            options.append(f"❌ {col} (already mapped)")
                        else:
                            options.append(f"✅ {col}")
                    
                    default_idx = 0
                    if auto_mapped and auto_mapped in primary_df.columns:
                        if auto_mapped in already_mapped_cols:
                            # If auto-mapped column is already taken, default to new column
                            default_idx = 0
                        else:
                            # Find the index of the auto-mapped column in options
                            for i, option in enumerate(options):
                                if option.endswith(f" {auto_mapped}") and not option.startswith("❌"):
                                    default_idx = i
                                    break
                    
                    selected = st.selectbox(
                        f"Map to:",
                        options,
                        index=default_idx,
                        key=f"mapping_{file_idx}_{sec_col}",
                        label_visibility="collapsed"
                    )
                    
                    # Update mapping with validation
                    if selected == "➕ Create as new column":
                        mappings[sec_col] = None
                    elif selected.startswith("❌"):
                        # User selected an already mapped column - show warning and keep previous mapping
                        st.warning(f"⚠️ This column is already mapped to by another column. Please choose a different option.")
                        # Keep the previous mapping or set to None
                        if sec_col in mappings and not mappings[sec_col] in already_mapped_cols:
                            # Keep previous mapping if it's not already taken
                            pass
                        else:
                            mappings[sec_col] = None
                    else:
                        # Extract column name from option (remove "✅ " prefix)
                        selected_col = selected.replace("✅ ", "")
                        mappings[sec_col] = selected_col
                
                st.divider()

    def _validate_mappings(self, mappings: Dict[str, Optional[str]]) -> Dict[str, List[str]]:
        """Validate mappings to detect duplicate column assignments."""
        duplicate_mappings = {}
        primary_mappings = {}
        
        for sec_col, pri_col in mappings.items():
            if pri_col:  # Only check non-None mappings
                if pri_col in primary_mappings:
                    # Duplicate mapping detected
                    if pri_col not in duplicate_mappings:
                        duplicate_mappings[pri_col] = [primary_mappings[pri_col]]
                    duplicate_mappings[pri_col].append(sec_col)
                else:
                    primary_mappings[pri_col] = sec_col
        
        return duplicate_mappings

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
            duplicate_mappings = {}  # Track multiple secondary columns mapping to same primary

            # First, handle explicitly mapped columns
            for sec_col, pri_col in mappings.items():
                if pri_col:  # Map to existing column
                    rename_map[sec_col] = pri_col
                    if pri_col not in used_names:
                        final_columns.append(pri_col)
                        used_names.add(pri_col)
                        duplicate_mappings[pri_col] = [sec_col]
                    else:
                        # Multiple secondary columns mapping to same primary column
                        duplicate_mappings[pri_col].append(sec_col)

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

            # Handle duplicate mappings by combining data from multiple secondary columns
            for pri_col, sec_cols in duplicate_mappings.items():
                if len(sec_cols) > 1:
                    # Multiple secondary columns mapping to same primary column
                    # Combine them by concatenating non-null values
                    combined_data = []
                    for sec_col in sec_cols:
                        if sec_col in secondary_work.columns:
                            col_data = secondary_work[sec_col].fillna('')
                            combined_data.append(col_data)
                    
                    if combined_data:
                        # Combine the data, prioritizing non-empty values
                        combined_series = pd.Series([''] * len(secondary_work), index=secondary_work.index)
                        for col_data in combined_data:
                            # Use non-empty values from each column
                            mask = (col_data != '') & (col_data.notna())
                            combined_series.loc[mask] = col_data.loc[mask]
                        
                        # Add the combined column
                        secondary_work[pri_col] = combined_series
                        
                        # Remove the individual secondary columns
                        for sec_col in sec_cols:
                            if sec_col in secondary_work.columns:
                                secondary_work = secondary_work.drop(columns=[sec_col])
                else:
                    # Single mapping, just rename
                    sec_col = sec_cols[0]
                    if sec_col in secondary_work.columns:
                        secondary_work = secondary_work.rename(columns={sec_col: pri_col})
            
            # Rename remaining secondary dataframe columns
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
            
            # Log the error
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

    def _analyze_column_similarity_optimized(self, col1_name: str, col1_data: pd.Series, col2_name: str, col2_data: pd.Series) -> Dict:
        """
        Optimized version of column similarity analysis with reduced computational overhead.
        Uses caching and early termination for better performance.
        """
        import re
        from difflib import SequenceMatcher
        
        report = {
            'name_similarity': 0.0,
            'data_similarity': 0.0,
            'score': 0.0,
            'match_details': []
        }
        
        # Quick name similarity check first (most important)
        name_similarity = self._calculate_name_similarity_fast(col1_name, col2_name)
        report['name_similarity'] = name_similarity
        
        # Early termination for very high name similarity
        if name_similarity > 0.95:
            report['score'] = name_similarity
            report['match_details'].append("High confidence name match")
            return report
        
        # Only calculate data similarity if name similarity is reasonable
        if name_similarity > 0.3:  # Only check data if names are somewhat similar
            data_similarity = self._calculate_data_similarity_optimized(col1_data, col2_data)
            report['data_similarity'] = data_similarity
            report['score'] = max(name_similarity, data_similarity * 0.7)
        else:
            report['score'] = name_similarity
        
        # Add match details
        if report['score'] > 0.5:
            if name_similarity > 0.8:
                report['match_details'].append("Good name match")
            if report['data_similarity'] > 0.5:
                report['match_details'].append("Similar data patterns")
        
        return report

    def _calculate_name_similarity_fast(self, col1_name: str, col2_name: str) -> float:
        """Fast name similarity calculation with caching."""
        # Check cache first
        cache_key = f"name|{col1_name}|{col2_name}"
        if cache_key in self._similarity_cache:
            return self._similarity_cache[cache_key]
        
        # Quick exact match
        if col1_name.lower().strip() == col2_name.lower().strip():
            self._similarity_cache[cache_key] = 1.0
            return 1.0
        
        # Clean names efficiently
        name1 = self._clean_column_name_cached(col1_name)
        name2 = self._clean_column_name_cached(col2_name)
        
        # Quick containment check
        if name1 in name2 or name2 in name1:
            score = 0.85
            self._similarity_cache[cache_key] = score
            return score
        
        # Sequence similarity (most expensive, do last)
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, name1, name2).ratio()
        
        # Cache and return
        self._similarity_cache[cache_key] = similarity
        return similarity

    def _clean_column_name_cached(self, name: str) -> str:
        """Clean column name with caching."""
        if name in self._column_variations_cache:
            return self._column_variations_cache[name]
        
        if not isinstance(name, str):
            name = str(name)
        
        # Fast cleaning - only essential operations
        import re
        cleaned = name.strip().lower()
        cleaned = re.sub(r'[-_\s\./\\]+', '_', cleaned)
        cleaned = re.sub(r'[^a-z0-9_]', '', cleaned)
        cleaned = re.sub(r'_+', '_', cleaned).strip('_')
        
        self._column_variations_cache[name] = cleaned
        return cleaned

    def _calculate_data_similarity_optimized(self, col1_data: pd.Series, col2_data: pd.Series) -> float:
        """Optimized data similarity calculation with reduced sampling."""
        try:
            # Handle empty or all-null columns
            if col1_data.isna().all() or col2_data.isna().all():
                return 0.0
            
            # Use smaller samples for faster processing
            sample_size = min(50, len(col1_data), len(col2_data))  # Reduced from 100
            sample1 = col1_data.dropna().head(sample_size)
            sample2 = col2_data.dropna().head(sample_size)
            
            if len(sample1) == 0 or len(sample2) == 0:
                return 0.0
            
            # Quick type compatibility check
            type1 = col1_data.dtype
            type2 = col2_data.dtype
            
            if type1 != type2:
                # Try to convert to same type for comparison
                try:
                    if pd.api.types.is_numeric_dtype(type1):
                        sample2 = pd.to_numeric(sample2, errors='coerce')
                    elif pd.api.types.is_numeric_dtype(type2):
                        sample1 = pd.to_numeric(sample1, errors='coerce')
                    else:
                        sample1 = sample1.astype(str)
                        sample2 = sample2.astype(str)
                except:
                    sample1 = sample1.astype(str)
                    sample2 = sample2.astype(str)
            
            # Calculate overlap of unique values (faster than full comparison)
            unique1 = set(sample1.unique())
            unique2 = set(sample2.unique())
            
            if not unique1 or not unique2:
                return 0.0
            
            intersection = len(unique1.intersection(unique2))
            union = len(unique1.union(unique2))
            
            # Jaccard similarity
            jaccard_sim = intersection / union if union > 0 else 0.0
            
            # Additional checks for numeric data
            if pd.api.types.is_numeric_dtype(sample1) and pd.api.types.is_numeric_dtype(sample2):
                # Check if ranges overlap
                range1 = (sample1.min(), sample1.max())
                range2 = (sample2.min(), sample2.max())
                
                if range1[1] >= range2[0] and range2[1] >= range1[0]:
                    jaccard_sim = max(jaccard_sim, 0.3)  # Bonus for overlapping ranges
            
            return min(1.0, jaccard_sim)
            
        except Exception:
            return 0.0

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
        """Prepare a dataframe for merging by ensuring consistent data types (optimized)."""
        # Use copy only if necessary
        df_copy = df.copy()
        
        # Process columns in batches for better performance
        object_cols = df_copy.select_dtypes(include=['object']).columns
        datetime_cols = df_copy.select_dtypes(include=['datetime64']).columns
        numeric_cols = df_copy.select_dtypes(include=['number']).columns
        
        # Handle datetime columns (fastest)
        if len(datetime_cols) > 0:
            df_copy[datetime_cols] = df_copy[datetime_cols].astype(str)
        
        # Handle numeric columns (fast)
        if len(numeric_cols) > 0:
            df_copy[numeric_cols] = df_copy[numeric_cols].apply(pd.to_numeric, errors='coerce')
        
        # Handle object columns (most complex, but optimized)
        if len(object_cols) > 0:
            for col in object_cols:
                try:
                    # Quick check for mixed types using smaller sample
                    sample_values = df_copy[col].dropna().head(5)  # Reduced sample size
                    if len(sample_values) > 0:
                        # Fast type detection
                        numeric_count = pd.to_numeric(sample_values, errors='coerce').notna().sum()
                        string_count = sum(isinstance(x, str) for x in sample_values if pd.notna(x))
                        
                        if numeric_count > 0 and string_count > 0:
                            # Mixed types - convert all to string
                            df_copy[col] = df_copy[col].astype(str)
                        elif numeric_count > 0:
                            # All numeric - convert to numeric
                            df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce')
                        else:
                            # All string - ensure consistent string type
                            df_copy[col] = df_copy[col].astype(str)
                    else:
                        # Empty column - keep as object
                        df_copy[col] = df_copy[col].astype(str)
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
