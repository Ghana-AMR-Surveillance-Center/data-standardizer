"""
File Merger Module
Handles merging of multiple Excel files with column mapping.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Tuple, Optional

class FileMerger:
    """Handles merging of Excel files with column mapping."""
    
    def _load_and_validate_file(self, file) -> Tuple[Optional[pd.DataFrame], Dict]:
        """
        Load a file and perform initial validation.
        
        Returns:
            Tuple of (DataFrame or None, validation results dict)
        """
        validation = {
            'success': False,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        try:
            if file.name.lower().endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Basic validation
            validation['stats'] = {
                'rows': len(df),
                'columns': len(df.columns),
                'missing_data': df.isna().sum().sum(),
                'duplicate_rows': df.duplicated().sum(),
                'memory_usage': df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
            }
            
            # Check for empty columns
            empty_cols = df.columns[df.isna().all()].tolist()
            if empty_cols:
                validation['warnings'].append(f"Found {len(empty_cols)} empty columns")
                validation['empty_columns'] = empty_cols
            
            # Check for duplicate column names
            if len(df.columns) != len(set(df.columns)):
                dupes = df.columns[df.columns.duplicated()].tolist()
                validation['errors'].append(f"Found duplicate column names: {', '.join(dupes)}")
            
            # Check data types
            validation['dtypes'] = df.dtypes.astype(str).to_dict()
            
            validation['success'] = len(validation['errors']) == 0
            return df, validation
            
        except Exception as e:
            validation['errors'].append(str(e))
            return None, validation

    def show_merger_interface(self) -> Optional[pd.DataFrame]:
        """Display the file merger interface with improved UX."""
        # Header with enhanced instructions
        st.markdown("""
        # 📊 Easy File Merger
        
        ### Merge your Excel and CSV files in 4 simple steps:
        
        1. 📁 **Drop your files** - Upload 2 or more Excel/CSV files
        2. 🔍 **Quick check** - We'll validate your files automatically
        3. 🔗 **Match columns** - Review or adjust how columns are matched
        4. ⬇️ **Download** - Get your merged file
        
        Need help? Click the '❓ Help' section below.
        """)
        
        # Help section
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
        
        # Progress tracking with better visuals
        progress_status = {
            1: "📁 Ready to upload",
            2: "🔍 Checking files",
            3: "🔗 Mapping columns",
            4: "✨ Complete!"
        }
        
        if 'merger_step' not in st.session_state:
            st.session_state.merger_step = 1
            
        # Visual progress bar
        current_step = st.session_state.merger_step
        st.progress(current_step/4)
        st.caption(f"Status: {progress_status[current_step]}")
        
        # Rest of the existing upload interface
        st.markdown("---")
        
        # Enhanced file uploader with clear instructions
        uploaded_files = st.file_uploader(
            "Drop your Excel or CSV files here",
            type=['xlsx', 'xls', 'csv'],
            accept_multiple_files=True,
            help="📌 The first file you upload will be used as the main template"
        )
        
        # More informative status messages
        if not uploaded_files:
            st.info("👆 Start by dropping two or more files above")
            return None
            
        if len(uploaded_files) < 2:
            st.warning("🎯 Almost there! Drop at least one more file to start merging")
            return None
            
        # New: Primary file selection
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
        
        st.session_state.merger_step = 2
        
        # Step 2: File Validation and Preview
        st.markdown("## 🔍 Step 2: File Validation")
        
        with st.spinner("🔄 Loading and validating files..."):
            dataframes = []
            file_info = []
            
            for i, file in enumerate(uploaded_files):
                df, validation = self._load_and_validate_file(file)
                
                if not validation['success']:
                    st.error(f"❌ Error loading {file.name}")
                    for error in validation['errors']:
                        st.error(f"• {error}")
                    return None
                
                dataframes.append(df)
                file_info.append({
                    'name': file.name,
                    'df': df,
                    'validation': validation
                })
        
        # Show file summary in a clean table
        summary_data = []
        for i, info in enumerate(file_info):
            summary_data.append({
                "File": f"📄 {info['name'][:30]}{'...' if len(info['name']) > 30 else ''}",
                "Rows": f"{info['validation']['stats']['rows']:,}",
                "Columns": info['validation']['stats']['columns'],
                "Status": "✅ Ready" if info['validation']['success'] else "❌ Error"
            })
        
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
        
        # File previews in tabs
        st.markdown("### 👀 File Previews")
        tabs = st.tabs([f"File {i+1}: {info['name'][:20]}" for i, info in enumerate(file_info)])
        
        for i, (tab, info) in enumerate(zip(tabs, file_info)):
            with tab:
                if i == 0:
                    st.info("🎯 **Primary file** - Other files will be merged into this structure")
                st.dataframe(info['df'].head(10), use_container_width=True)
        
        st.session_state.merger_step = 3
        
        # Step 3: Column Mapping
        st.markdown("## 🔗 Step 3: Column Mapping")
        
        primary_df = dataframes[0]
        all_merged_data = primary_df.copy()
        
        # Simple mapping interface for each secondary file
        for file_idx, secondary_df in enumerate(dataframes[1:], 1):
            with st.expander(f"🔧 Map columns for File {file_idx + 1}: {file_info[file_idx]['name']}", expanded=True):
                
                st.markdown(f"**Merging:** {file_info[file_idx]['name']} → {file_info[0]['name']}")
                
                # Auto-generate mappings
                mappings = self._generate_smart_mappings(primary_df, secondary_df)
                
                # Show mapping results
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Mapping statistics
                    auto_mapped = len([m for m in mappings.values() if m is not None])
                    new_columns = len(mappings) - auto_mapped
                    
                    st.metric("🎯 Auto-mapped", auto_mapped)
                    st.metric("🆕 New columns", new_columns)
                    st.metric("📊 Total columns", len(mappings))
                
                with col2:
                    # Quick review option
                    review_mode = st.radio(
                        "Review options:",
                        ["✅ Accept automatic mapping", "🔍 Review each column"],
                        key=f"review_mode_{file_idx}",
                        horizontal=True
                    )
                
                # Show mappings based on user choice
                if review_mode == "🔍 Review each column":
                    self._show_detailed_mapping_interface(primary_df, secondary_df, mappings, file_idx)
                else:
                    # Show summary of automatic mappings
                    self._show_mapping_summary(mappings, file_idx)
                
                # Apply mappings and merge
                try:
                    merged_data = self._apply_mappings_and_merge(all_merged_data, secondary_df, mappings)
                    all_merged_data = merged_data
                    st.success(f"✅ Successfully mapped and merged File {file_idx + 1}")
                except Exception as e:
                    st.error(f"❌ Error merging File {file_idx + 1}: {str(e)}")
                    return None
        
        st.session_state.merger_step = 4
        
        # Step 4: Final Result
        st.markdown("## 🎉 Step 4: Merge Complete!")
        
        # Final statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📄 Files merged", len(uploaded_files))
        with col2:
            st.metric("📊 Total rows", f"{len(all_merged_data):,}")
        with col3:
            st.metric("📋 Total columns", len(all_merged_data.columns))
        with col4:
            total_original = sum(len(df) for df in dataframes)
            duplicates_removed = total_original - len(all_merged_data)
            st.metric("🗑️ Duplicates removed", f"{duplicates_removed:,}")
        
        # Preview merged data
        st.markdown("### 👀 Preview Merged Data")
        st.dataframe(all_merged_data.head(20), use_container_width=True)
        
        # Success message and return
        st.success("🎊 **Merge completed successfully!** You can now download your merged file using the download button in the sidebar.")
        
        return all_merged_data

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
        """Show an enhanced summary of automatic mappings."""
        st.markdown("#### 📋 Column Mapping Summary")
        
        # Group mappings by status
        merged_cols = []
        new_cols = []
        for sec_col, pri_col in mappings.items():
            if pri_col:
                merged_cols.append({
                    "From": sec_col,
                    "To": pri_col,
                    "Status": "✅ Will merge"
                })
            else:
                new_cols.append({
                    "From": sec_col,
                    "To": "New column",
                    "Status": "➕ Will add"
                })
        
        # Show statistics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🔗 Columns to merge", len(merged_cols))
        with col2:
            st.metric("➕ New columns", len(new_cols))
        
        # Show detailed mapping table with better formatting
        st.dataframe(
            pd.DataFrame(merged_cols + new_cols),
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
        # Create working copy
        secondary_work = secondary_df.copy()
        
        # Keep track of used column names to handle duplicates
        used_column_names = set()
        rename_map = {}
        
        # First pass: map columns that have explicit mappings
        for sec_col, pri_col in mappings.items():
            if pri_col:  # Map to existing column
                rename_map[sec_col] = pri_col
                used_column_names.add(pri_col)
        
        # Second pass: handle unmapped columns that might have name conflicts
        for sec_col in secondary_df.columns:
            if sec_col not in rename_map:  # This is a new column
                new_col_name = sec_col
                if new_col_name in used_column_names:
                    # If name exists, append a suffix
                    counter = 1
                    while f"{new_col_name}_{counter}" in used_column_names:
                        counter += 1
                    new_col_name = f"{new_col_name}_{counter}"
                rename_map[sec_col] = new_col_name
                used_column_names.add(new_col_name)
        
        # Apply all renames at once
        secondary_work = secondary_work.rename(columns=rename_map)
        
        # Create primary work copy and ensure it has all needed columns
        primary_work = primary_df.copy()
        
        # Add missing columns to both dataframes
        all_columns = list(set(primary_work.columns) | set(secondary_work.columns))
        
        for col in all_columns:
            if col not in primary_work.columns:
                primary_work[col] = None
            if col not in secondary_work.columns:
                secondary_work[col] = None
        
        # Ensure both dataframes have exactly the same columns in the same order
        primary_work = primary_work[all_columns]
        secondary_work = secondary_work[all_columns]
        
        # Merge the dataframes
        merged = pd.concat([primary_work, secondary_work], ignore_index=True, sort=False)
        
        # Remove duplicates
        merged = merged.drop_duplicates()
        
        return merged

    def analyze_column_similarity(self, col1_name: str, col1_data: pd.Series, col2_name: str, col2_data: pd.Series) -> Dict:
        """
        Analyze similarity between two columns based on name similarity only.
        Returns a similarity report focused on name matching.
        """
        import re
        from difflib import SequenceMatcher
        
        report = {
            'name_similarity': 0.0,
            'score': 0.0,
            'match_details': []
        }
        
        def clean_column_name(name):
            """Clean and standardize column names with enhanced whitespace and case handling."""
            if not isinstance(name, str):
                name = str(name)
                
            # Thorough whitespace and character cleaning
            name = name.strip()
            name = re.sub(r'\s+', ' ', name)
            name = ''.join(char for char in name if char.isprintable())
            name = name.lower()
            
            # Special character handling
            name = re.sub(r'[-_\s\./\\]+', '_', name)
            name = re.sub(r'[^a-z0-9_]', '', name)
            
            # Remove common prefixes/suffixes
            prefixes_suffixes = ['id', 'code', 'dt', 'date', 'num', 'number', 'col', 'column', 'field', 'value']
            
            for prefix in prefixes_suffixes:
                name = re.sub(f'^{prefix}_', '', name)
                name = re.sub(f'_{prefix}$', '', name)
            
            # Final cleanup
            name = name.strip('_')
            name = re.sub(r'_+', '_', name)
            
            return name
        
        def get_name_variations(name):
            """Get common variations of column names including AST-specific patterns."""
            variations = {name}
            
            # Medical/lab data variations
            replacements = {
                'id': ['identifier', 'identity', 'code', 'number', 'no', 'num'],
                'dob': ['date_of_birth', 'birth_date', 'birthdate', 'birth'],
                'org': ['organism', 'organization', 'micro_organism'],
                'spec': ['specimen', 'species', 'sample', 'isolate'],
                'lab': ['laboratory', 'laboratories', 'facility'],
                'hosp': ['hospital', 'hospitalization', 'facility', 'center', 'centre'],
                'pat': ['patient', 'pathogen', 'person', 'subject'],
                'res': ['result', 'resistance', 'resistant', 'response', 'test'],
                'sens': ['sensitive', 'sensitivity', 'susceptible', 'susceptibility'],
                'ab': ['antibiotic', 'antibacterial', 'antimicrobial', 'drug'],
                'mic': ['minimum_inhibitory_concentration', 'min_inhib_conc'],
                'int': ['interpretation', 'result', 'sir'],
                'sir': ['susceptibility', 'interpretation', 'result'],
                'nd': ['disk', 'disc', 'concentration'],
            }
            
            # Generate variations
            for abbr, full_forms in replacements.items():
                if abbr in name:
                    for full in full_forms:
                        variations.add(name.replace(abbr, full))
                for full in full_forms:
                    if full in name:
                        variations.add(name.replace(full, abbr))
            
            # Handle plural forms and separators
            if name.endswith('s'):
                variations.add(name[:-1])
            else:
                variations.add(name + 's')
            
            separators = ['_', ' ', '-', '.']
            words = re.split(r'[_\s\-\.]+', name)
            for sep in separators:
                variations.add(sep.join(words))
            
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
        
        # Set final scores and details
        report['name_similarity'] = best_score
        report['score'] = best_score
        
        if report['score'] > 0:
            if exact_match:
                report['match_details'].append("Exact name match")
            elif variation_match:
                report['match_details'].append("Common variation match")
            elif contains:
                report['match_details'].append("Name containment match")
            elif sequence_similarity > 0.5:
                report['match_details'].append(f"Similar names ({sequence_similarity:.0%} match)")
        else:
            report['match_details'].append(f"Partial match (similarity: {sequence_similarity:.2f})")
        
        # Set final scores
        report['name_similarity'] = best_score
        report['score'] = best_score
        
        # Add detailed explanation if needed
        if report['score'] > 0:
            if exact_match:
                report['match_details'].append("Exact name match")
            elif variation_match:
                report['match_details'].append("Common variation match")
            elif contains:
                report['match_details'].append("Name containment match")
            elif sequence_similarity > 0.5:
                report['match_details'].append(f"Similar names ({sequence_similarity:.0%} match)")
        else:
            report['match_details'].append(f"Partial match (similarity: {sequence_similarity:.2f})")
        
        return report
