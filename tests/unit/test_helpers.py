"""
Unit tests for utils.helpers module.
"""

import pytest
import pandas as pd
from utils.helpers import (
    clean_column_name,
    standardize_value,
    detect_date_format,
    parse_age_value,
    convert_age_to_years,
)


class TestCleanColumnName:
    """Tests for clean_column_name function."""
    
    def test_clean_basic_name(self):
        """Test cleaning a basic column name."""
        assert clean_column_name("Column Name") == "column_name"
    
    def test_clean_with_special_chars(self):
        """Test cleaning name with special characters."""
        assert clean_column_name("Column-Name_123") == "column_name_123"
    
    def test_clean_with_spaces(self):
        """Test cleaning name with multiple spaces."""
        assert clean_column_name("Column   Name") == "column_name"


class TestStandardizeValue:
    """Tests for standardize_value function."""
    
    def test_standardize_string(self):
        """Test standardizing a string value."""
        assert standardize_value("  test  ") == "test"
    
    def test_standardize_nan(self):
        """Test standardizing NaN value."""
        assert standardize_value(pd.NA) is None
        assert standardize_value(None) is None
    
    def test_standardize_numeric(self):
        """Test standardizing numeric value."""
        assert standardize_value(42) == 42


class TestDetectDateFormat:
    """Tests for detect_date_format function."""
    
    def test_detect_iso_format(self):
        """Test detecting ISO date format."""
        series = pd.Series(['2024-01-01', '2024-01-02', '2024-01-03'])
        assert detect_date_format(series) == '%Y-%m-%d'
    
    def test_detect_slash_format(self):
        """Test detecting date format with slashes."""
        series = pd.Series(['01/01/2024', '02/01/2024', '03/01/2024'])
        result = detect_date_format(series)
        assert result in ['%d/%m/%Y', '%m/%d/%Y']
    
    def test_detect_no_format(self):
        """Test with non-date values."""
        series = pd.Series(['not', 'a', 'date'])
        assert detect_date_format(series) is None
    
    def test_detect_empty_series(self):
        """Test with empty series."""
        series = pd.Series([], dtype=object)
        assert detect_date_format(series) is None


class TestParseAgeValue:
    """Tests for parse_age_value function."""
    
    def test_parse_days(self):
        """Test parsing age in days."""
        value, unit, orig = parse_age_value("6D")
        assert value == 6.0
        assert unit == "D"
        assert orig == "6D"
    
    def test_parse_months(self):
        """Test parsing age in months."""
        value, unit, orig = parse_age_value("67M")
        assert value == 67.0
        assert unit == "M"
    
    def test_parse_with_comparison(self):
        """Test parsing age with comparison operator."""
        value, unit, orig = parse_age_value("<67M")
        assert value == pytest.approx(66.33, rel=0.01)
        assert unit == "M"
    
    def test_parse_invalid(self):
        """Test parsing invalid age string."""
        value, unit, orig = parse_age_value("invalid")
        assert value is None


class TestConvertAgeToYears:
    """Tests for convert_age_to_years function."""
    
    def test_convert_days(self):
        """Test converting days to years."""
        assert convert_age_to_years(365, 'D') == pytest.approx(1.0)
    
    def test_convert_months(self):
        """Test converting months to years."""
        assert convert_age_to_years(12, 'M') == pytest.approx(1.0)
    
    def test_convert_weeks(self):
        """Test converting weeks to years."""
        assert convert_age_to_years(52, 'W') == pytest.approx(1.0)
    
    def test_convert_years(self):
        """Test converting years (no conversion needed)."""
        assert convert_age_to_years(5, 'Y') == 5.0



