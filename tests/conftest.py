"""
Pytest configuration and shared fixtures for GLASS Data Standardizer tests.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'age': [25, 30, 35, 28, 32],
        'value': [100.5, 200.3, 150.0, 175.8, 210.2]
    })


@pytest.fixture
def sample_dataframe_with_dates():
    """Create a sample DataFrame with date columns."""
    dates = pd.date_range('2024-01-01', periods=5, freq='D')
    return pd.DataFrame({
        'date': dates,
        'value': [10, 20, 30, 40, 50]
    })


@pytest.fixture
def sample_dataframe_with_nulls():
    """Create a sample DataFrame with null values."""
    return pd.DataFrame({
        'col1': [1, 2, None, 4, 5],
        'col2': ['a', None, 'c', 'd', 'e'],
        'col3': [1.1, 2.2, 3.3, None, 5.5]
    })


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for file operations."""
    return tmp_path



