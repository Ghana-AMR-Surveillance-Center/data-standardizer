"""
Column name utilities for case-insensitive matching and whitespace handling
"""

from typing import List, Dict, Optional, Set
import pandas as pd


def normalize_column_name(col_name: str) -> str:
    """
    Normalize column name for case-insensitive matching.
    Strips leading/trailing whitespace and converts to lowercase.
    
    Args:
        col_name: Column name to normalize
        
    Returns:
        Normalized column name (lowercase, stripped)
    """
    if not isinstance(col_name, str):
        col_name = str(col_name)
    return col_name.strip().lower()


def normalize_column_names(columns: List[str]) -> List[str]:
    """
    Normalize a list of column names.
    
    Args:
        columns: List of column names
        
    Returns:
        List of normalized column names
    """
    return [normalize_column_name(col) for col in columns]


def find_column_case_insensitive(df: pd.DataFrame, target_col: str) -> Optional[str]:
    """
    Find a column in dataframe using case-insensitive matching with whitespace stripping.
    
    Args:
        df: DataFrame to search
        target_col: Column name to find (case-insensitive)
        
    Returns:
        Actual column name if found, None otherwise
    """
    target_normalized = normalize_column_name(target_col)
    
    for col in df.columns:
        if normalize_column_name(col) == target_normalized:
            return col
    
    return None


def find_columns_case_insensitive(df: pd.DataFrame, target_cols: List[str]) -> Dict[str, Optional[str]]:
    """
    Find multiple columns in dataframe using case-insensitive matching.
    
    Args:
        df: DataFrame to search
        target_cols: List of column names to find (case-insensitive)
        
    Returns:
        Dictionary mapping normalized target names to actual column names (or None if not found)
    """
    result = {}
    target_normalized_set = {normalize_column_name(col): col for col in target_cols}
    
    for col in df.columns:
        col_normalized = normalize_column_name(col)
        if col_normalized in target_normalized_set:
            result[target_normalized_set[col_normalized]] = col
    
    # Add None for columns not found
    for target_col in target_cols:
        if target_col not in result:
            result[target_col] = None
    
    return result


def match_column_name(source_col: str, target_col: str) -> bool:
    """
    Check if two column names match (case-insensitive, whitespace-insensitive).
    
    Args:
        source_col: Source column name
        target_col: Target column name
        
    Returns:
        True if columns match (case-insensitive, whitespace-insensitive)
    """
    return normalize_column_name(source_col) == normalize_column_name(target_col)


def contains_column_case_insensitive(df: pd.DataFrame, target_col: str) -> bool:
    """
    Check if dataframe contains a column (case-insensitive, whitespace-insensitive).
    
    Args:
        df: DataFrame to check
        target_col: Column name to check for
        
    Returns:
        True if column exists (case-insensitive)
    """
    return find_column_case_insensitive(df, target_col) is not None


def get_column_case_insensitive(df: pd.DataFrame, target_col: str) -> Optional[pd.Series]:
    """
    Get a column from dataframe using case-insensitive matching.
    
    Args:
        df: DataFrame
        target_col: Column name to get (case-insensitive)
        
    Returns:
        Series if found, None otherwise
    """
    actual_col = find_column_case_insensitive(df, target_col)
    if actual_col:
        return df[actual_col]
    return None


def rename_columns_case_insensitive(df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Rename columns using case-insensitive matching.
    
    Args:
        df: DataFrame to rename columns in
        column_mapping: Dictionary mapping target names to new names
        (matching is case-insensitive)
        
    Returns:
        DataFrame with renamed columns
    """
    df_copy = df.copy()
    rename_map = {}
    
    for target_col, new_name in column_mapping.items():
        actual_col = find_column_case_insensitive(df_copy, target_col)
        if actual_col:
            rename_map[actual_col] = new_name
    
    if rename_map:
        df_copy = df_copy.rename(columns=rename_map)
    
    return df_copy


def normalize_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize all column names in a dataframe (strip whitespace, lowercase).
    
    Args:
        df: DataFrame to normalize
        
    Returns:
        DataFrame with normalized column names
    """
    df_copy = df.copy()
    df_copy.columns = [normalize_column_name(col) for col in df_copy.columns]
    return df_copy


def get_columns_matching_pattern(df: pd.DataFrame, pattern: str, case_sensitive: bool = False) -> List[str]:
    """
    Get columns matching a pattern (case-insensitive by default).
    
    Args:
        df: DataFrame to search
        pattern: Pattern to match (substring)
        case_sensitive: Whether matching should be case-sensitive
        
    Returns:
        List of matching column names
    """
    import re
    
    if case_sensitive:
        pattern_compiled = re.compile(pattern)
        return [col for col in df.columns if pattern_compiled.search(col)]
    else:
        pattern_lower = pattern.lower()
        return [col for col in df.columns if pattern_lower in normalize_column_name(col)]


def standardize_column_access(df: pd.DataFrame, column_name: str) -> Optional[pd.Series]:
    """
    Standardized column access with case-insensitive matching and whitespace handling.
    
    Args:
        df: DataFrame
        column_name: Column name to access (case-insensitive)
        
    Returns:
        Series if found, None otherwise
    """
    actual_col = find_column_case_insensitive(df, column_name)
    if actual_col:
        return df[actual_col]
    return None

