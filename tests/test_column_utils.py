"""
Unit tests for column_utils module.
"""

import os
import sys
import unittest

import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.column_utils import (
    normalize_column_name,
    normalize_column_names,
    find_column_case_insensitive,
)


class TestColumnUtils(unittest.TestCase):
    """Tests for column utilities."""

    def test_normalize_column_name(self):
        """Test column name normalization."""
        self.assertEqual(normalize_column_name("  Patient_ID  "), "patient_id")
        self.assertEqual(normalize_column_name("ORGANISM"), "organism")
        self.assertEqual(normalize_column_name("Specimen_Type"), "specimen_type")

    def test_normalize_column_names(self):
        """Test list normalization."""
        cols = ["  Col1  ", "COL2", "col3"]
        result = normalize_column_names(cols)
        self.assertEqual(result, ["col1", "col2", "col3"])

    def test_find_column_case_insensitive_found(self):
        """Test case-insensitive column lookup finds column."""
        df = pd.DataFrame({"Patient_ID": [1, 2], "Organism": ["A", "B"]})
        self.assertEqual(find_column_case_insensitive(df, "patient_id"), "Patient_ID")
        self.assertEqual(find_column_case_insensitive(df, "ORGANISM"), "Organism")

    def test_find_column_case_insensitive_not_found(self):
        """Test case-insensitive column lookup returns None when not found."""
        df = pd.DataFrame({"Patient_ID": [1, 2]})
        self.assertIsNone(find_column_case_insensitive(df, "nonexistent"))
        self.assertIsNone(find_column_case_insensitive(df, "organism"))

    def test_find_column_with_whitespace(self):
        """Test column lookup handles whitespace in target."""
        df = pd.DataFrame({"  Patient_ID  ": [1, 2]})
        result = find_column_case_insensitive(df, "  patient_id  ")
        self.assertEqual(result, "  Patient_ID  ")


if __name__ == '__main__':
    unittest.main()
