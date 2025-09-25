"""
Data Transformer Module
Handles data transformation operations.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional

class DataTransformer:
    """Handles data transformation operations."""
    
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
        
        # Update current columns tracking
        st.session_state['transformation_state']['current_columns'] = list(df.columns)
        
        # Show current dataset status at the top
        original_count = len(st.session_state['transformation_state']['original_columns'])
        current_count = len(df.columns)
        operations_count = len(st.session_state['transformation_state'].get('operations_applied', []))
        
        if current_count != original_count or operations_count > 0:
            st.info(f"📊 Dataset Status: {len(df)} rows × {current_count} columns "
                   f"(Started with {original_count} columns, {operations_count} operations applied)")
            
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
                    
                    # Debug info to verify the fix
                    st.info(f"🔍 Debug: Session state now has {len(st.session_state['processed_data'].columns)} columns")
                    
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
