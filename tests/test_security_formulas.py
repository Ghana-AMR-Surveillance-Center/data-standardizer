"""
Unit tests for CSV/Excel formula injection sanitization.
"""

import os
import sys
import unittest

import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.security import sanitize_dataframe_formulas


class TestFormulaSanitization(unittest.TestCase):
    """Tests for formula injection sanitization."""

    def test_sanitize_formula_prefix_equals(self):
        """Test cells starting with = are sanitized."""
        df = pd.DataFrame({'a': ['=SUM(A1:A10)', 'normal', '=CMD|calc']})
        result = sanitize_dataframe_formulas(df)
        self.assertTrue(result['a'].iloc[0].startswith("'"))
        self.assertEqual(result['a'].iloc[1], 'normal')
        self.assertTrue(result['a'].iloc[2].startswith("'"))

    def test_sanitize_formula_prefix_plus(self):
        """Test cells starting with + are sanitized."""
        df = pd.DataFrame({'x': ['+1+1', 'valid']})
        result = sanitize_dataframe_formulas(df)
        self.assertTrue(result['x'].iloc[0].startswith("'"))

    def test_sanitize_formula_prefix_at(self):
        """Test cells starting with @ are sanitized."""
        df = pd.DataFrame({'y': ['@SUM(1,2)', 'ok']})
        result = sanitize_dataframe_formulas(df)
        self.assertTrue(result['y'].iloc[0].startswith("'"))

    def test_safe_cells_unchanged(self):
        """Test normal cells are not modified."""
        df = pd.DataFrame({'a': ['hello', '123', 'E. coli', 'S']})
        result = sanitize_dataframe_formulas(df)
        self.assertEqual(list(result['a']), ['hello', '123', 'E. coli', 'S'])

    def test_empty_dataframe(self):
        """Test empty DataFrame is returned unchanged."""
        df = pd.DataFrame()
        result = sanitize_dataframe_formulas(df)
        self.assertTrue(result.empty)

    def test_numeric_cells_unchanged(self):
        """Test numeric cells are not modified."""
        df = pd.DataFrame({'n': [1, 2.5, -3]})
        result = sanitize_dataframe_formulas(df)
        pd.testing.assert_series_equal(result['n'], df['n'])


if __name__ == '__main__':
    unittest.main()
