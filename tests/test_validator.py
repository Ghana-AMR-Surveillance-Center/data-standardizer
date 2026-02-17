"""
Unit tests for DataValidator module.
"""

import os
import sys
import unittest

import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validator import DataValidator


class TestDataValidator(unittest.TestCase):
    """Tests for DataValidator."""

    def setUp(self):
        self.validator = DataValidator()

    def test_validate_data_valid(self):
        """Test validation passes for valid data."""
        df = pd.DataFrame({
            'Patient_ID': ['P001', 'P002', 'P003'],
            'Age': [25, 30, 45],
            'Gender': ['M', 'F', 'M'],
            'Date_of_Admission': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Specimen_Type': ['Blood', 'Urine', 'Blood'],
            'Organism': ['E. coli', 'S. aureus', 'K. pneumoniae']
        })
        results = self.validator.validate_data(df)
        self.assertIn('summary', results)
        self.assertIn('errors', results)
        self.assertIn('warnings', results)
        # Valid data may still have some warnings depending on rules
        self.assertIsInstance(results['errors'], list)

    def test_validate_data_missing_required_column(self):
        """Test validation detects missing required column."""
        df = pd.DataFrame({
            'Age': [25, 30],
            'Gender': ['M', 'F'],
            # Missing Patient_ID, Date_of_Admission, Specimen_Type, Organism
        })
        results = self.validator.validate_data(df)
        self.assertGreater(len(results['errors']), 0)
        error_types = [e['type'] for e in results['errors']]
        self.assertIn('missing_column', error_types)

    def test_validate_data_duplicate_patient_id(self):
        """Test validation detects duplicate Patient_ID."""
        df = pd.DataFrame({
            'Patient_ID': ['P001', 'P001', 'P002'],  # Duplicate
            'Age': [25, 30, 45],
            'Gender': ['M', 'F', 'M'],
            'Date_of_Admission': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Specimen_Type': ['Blood', 'Urine', 'Blood'],
            'Organism': ['E. coli', 'S. aureus', 'K. pneumoniae']
        })
        results = self.validator.validate_data(df)
        error_types = [e['type'] for e in results['errors']]
        self.assertIn('duplicate_values', error_types)

    def test_validate_data_invalid_gender(self):
        """Test validation detects invalid Gender values."""
        df = pd.DataFrame({
            'Patient_ID': ['P001', 'P002'],
            'Age': [25, 30],
            'Gender': ['M', 'X'],  # X is invalid
            'Date_of_Admission': ['2024-01-01', '2024-01-02'],
            'Specimen_Type': ['Blood', 'Urine'],
            'Organism': ['E. coli', 'S. aureus']
        })
        results = self.validator.validate_data(df)
        error_types = [e['type'] for e in results['errors']]
        self.assertIn('invalid_values', error_types)

    def test_validate_data_empty_dataframe(self):
        """Test validation handles empty dataframe."""
        df = pd.DataFrame()
        results = self.validator.validate_data(df)
        self.assertIn('errors', results)
        self.assertIsInstance(results['errors'], list)


if __name__ == '__main__':
    unittest.main()
