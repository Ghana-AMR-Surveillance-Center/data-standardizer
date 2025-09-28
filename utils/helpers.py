"""
Utilities Module
Common utilities and helper functions.
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
import re

def prepare_df_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare DataFrame for display by converting problematic types.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with converted types for display
    """
    df = df.copy()
    
    # Convert mixed-type columns to appropriate types
    for col in df.columns:
        try:
            if df[col].dtype == 'object':
                # Check if column contains mixed types that cause Arrow issues
                sample_values = df[col].dropna().head(10)
                if len(sample_values) > 0:
                    # Check for mixed numeric and string types
                    has_numeric = any(pd.to_numeric(sample_values, errors='coerce').notna())
                    has_string = any(isinstance(x, str) for x in sample_values if pd.notna(x))
                    
                    if has_numeric and has_string:
                        # Mixed types - convert all to string for consistency
                        df[col] = df[col].astype(str)
                    elif has_numeric:
                        # All numeric - convert to numeric
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    else:
                        # All string - ensure consistent string type
                        df[col] = df[col].astype(str)
                else:
                    # Empty column - keep as object
                    df[col] = df[col].astype(str)
            else:
                # For non-object columns, ensure they're Arrow-compatible
                if df[col].dtype == 'datetime64[ns]':
                    # Convert datetime to string for Arrow compatibility
                    df[col] = df[col].astype(str)
                elif 'int' in str(df[col].dtype):
                    # Ensure integer columns are properly typed
                    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
                elif 'float' in str(df[col].dtype):
                    # Ensure float columns are properly typed
                    df[col] = pd.to_numeric(df[col], errors='coerce')
        except Exception:
            # If any conversion fails, convert to string as fallback
            df[col] = df[col].astype(str)
    
    return df

def clean_column_name(name: str) -> str:
    """
    Clean a column name to a standardized format.
    
    Args:
        name: Original column name
        
    Returns:
        Cleaned column name
    """
    # Remove special characters and replace spaces with underscores
    clean = re.sub(r'[^\w\s-]', '', name)
    clean = re.sub(r'[-\s]+', '_', clean)
    
    # Convert to lowercase and remove leading/trailing underscores
    return clean.lower().strip('_')

def standardize_value(value: Any) -> Any:
    """
    Standardize a value based on its type.
    
    Args:
        value: Value to standardize
        
    Returns:
        Standardized value
    """
    if pd.isna(value):
        return None
    elif isinstance(value, str):
        return value.strip()
    return value

def detect_date_format(series: pd.Series) -> Optional[str]:
    """
    Detect the date format in a series.
    
    Args:
        series: Series containing dates
        
    Returns:
        Date format string or None if no consistent format found
    """
    # Implementation remains the same...
    return None

def parse_age_value(age_str: str) -> Tuple[Optional[float], str, str]:
    """
    Parse an age string into a numeric value and unit.
    
    Args:
        age_str: Age string (e.g., '6D', '67M', '<67M')
        
    Returns:
        Tuple containing:
            - Numeric value (or None if invalid)
            - Unit (D=days, W=weeks, M=months, Y=years)
            - Original value for reference
    """
    if pd.isna(age_str) or not isinstance(age_str, str):
        return None, '', str(age_str)
    
    # Clean the input string
    age_str = age_str.strip().upper()
    original = age_str
    
    # Handle special cases like '<67M'
    comparison = ''
    if age_str.startswith('<'):
        comparison = '<'
        age_str = age_str[1:]
    elif age_str.startswith('>'):
        comparison = '>'
        age_str = age_str[1:]
    
    # Extract numeric value and unit
    match = re.match(r'^(\d+\.?\d*)\s*([DWMY])$', age_str)
    if not match:
        return None, '', original
    
    value, unit = match.groups()
    try:
        value = float(value)
        if comparison == '<':
            value = value * 0.99  # Just under the specified value
        elif comparison == '>':
            value = value * 1.01  # Just over the specified value
        return value, unit, original
    except ValueError:
        return None, '', original

def convert_age_to_years(age_value: float, unit: str) -> float:
    """
    Convert an age value to years based on its unit.
    
    Args:
        age_value: Numeric age value
        unit: Unit of age (D=days, W=weeks, M=months, Y=years)
        
    Returns:
        Age in years
    """
    if unit == 'Y' or not unit:
        return age_value
    elif unit == 'M':
        return age_value / 12
    elif unit == 'W':
        return age_value / 52
    elif unit == 'D':
        return age_value / 365
    return age_value

def preview_age_conversions(df: pd.DataFrame, age_column: str) -> pd.DataFrame:
    """
    Create a preview of age conversions.
    
    Args:
        df: Input dataframe
        age_column: Name of the age column
        
    Returns:
        DataFrame with original and converted ages
    """
    if age_column not in df.columns:
        return pd.DataFrame()
    
    # Create results dataframe
    results = []
    for original in df[age_column].dropna().unique():
        if pd.isna(original):
            continue
            
        value, unit, _ = parse_age_value(str(original))
        if value is not None:
            years = convert_age_to_years(value, unit)
            # Ensure numeric value
            try:
                years = float(years)
                results.append({
                    'Original': original,
                    'Converted (Years)': round(years, 2),
                    'Interpretation': f"{value} {unit} → {years:.2f} years"
                })
            except (ValueError, TypeError):
                continue
    
    return pd.DataFrame(results)

def convert_age_column(df: pd.DataFrame, age_column: str, approved_conversions: Dict[str, float]) -> pd.DataFrame:
    """
    Apply approved age conversions to the dataframe.
    
    Args:
        df: Input dataframe
        age_column: Name of the age column
        approved_conversions: Dictionary mapping original values to approved converted values
        
    Returns:
        DataFrame with converted ages
    """
    df = df.copy()
    
    def convert_value(x):
        if pd.isna(x):
            return pd.NA
        str_x = str(x)
        if str_x in approved_conversions:
            try:
                return float(approved_conversions[str_x])
            except (ValueError, TypeError):
                return pd.NA
        return x
    
    # Replace values in original column
    df[age_column] = df[age_column].apply(convert_value)
    
    # Ensure the column is numeric
    df[age_column] = pd.to_numeric(df[age_column], errors='coerce')
    
    # Store original values in a backup column
    df[f"{age_column}_original"] = df[age_column]
    
    return df

def detect_date_format(series: pd.Series) -> Optional[str]:
    """
    Detect the date format in a series.
    
    Args:
        series: Series containing dates
        
    Returns:
        Detected date format string or None
    """
    common_formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%Y/%m/%d',
        '%d-%m-%Y',
        '%m-%d-%Y'
    ]
    
    # Get non-null sample
    sample = series.dropna().head(100)
    if len(sample) == 0:
        return None
    
    # Try each format
    for fmt in common_formats:
        try:
            pd.to_datetime(sample, format=fmt)
            return fmt
        except ValueError:
            continue
    
    return None

def is_categorical(series: pd.Series, threshold: float = 0.05) -> bool:
    """
    Check if a series appears to be categorical.
    
    Args:
        series: Series to check
        threshold: Maximum ratio of unique values to total values
        
    Returns:
        bool: Whether the series appears categorical
    """
    if series.dtype == 'object':
        unique_ratio = series.nunique() / len(series)
        return unique_ratio <= threshold
    return False

def validate_email(email: str) -> bool:
    """
    Validate an email address.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: Whether the email is valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    Validate a phone number.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        bool: Whether the phone number is valid
    """
    # Remove common separators
    clean = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if remaining string is numeric and of reasonable length
    return clean.isdigit() and 8 <= len(clean) <= 15

def generate_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary statistics for a dataframe.
    
    Args:
        df: Input dataframe
        
    Returns:
        Dict containing summary statistics
    """
    summary = {
        'row_count': len(df),
        'column_count': len(df.columns),
        'missing_cells': df.isna().sum().sum(),
        'duplicate_rows': df.duplicated().sum()
    }
    
    # Add column type counts
    type_counts = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            type_counts['numeric'] = type_counts.get('numeric', 0) + 1
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            type_counts['date'] = type_counts.get('date', 0) + 1
        else:
            type_counts['text'] = type_counts.get('text', 0) + 1
    
    summary['column_types'] = type_counts
    
    # Calculate total memory usage
    summary['memory_mb'] = df.memory_usage(deep=True).sum() / 1024**2
    
    return summary
