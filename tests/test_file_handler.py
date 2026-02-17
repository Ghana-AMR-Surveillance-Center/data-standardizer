"""
Unit tests for FileHandler module.
"""

import io
import os
import sys
import tempfile
import unittest

import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_handler import FileHandler


class TestFileHandler(unittest.TestCase):
    """Tests for FileHandler."""

    def setUp(self):
        self.handler = FileHandler()

    def test_read_file_csv(self):
        """Test reading a CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1,col2\n1,2\n3,4\n")
            path = f.name
        try:
            df = self.handler.read_file(path)
            self.assertIsNotNone(df)
            self.assertEqual(len(df), 2)
            self.assertEqual(list(df.columns), ['col1', 'col2'])
        finally:
            os.unlink(path)

    def test_read_file_nonexistent(self):
        """Test reading a non-existent file returns None."""
        df = self.handler.read_file("/nonexistent/path/file.csv")
        self.assertIsNone(df)

    def test_read_file_unsupported_format(self):
        """Test reading unsupported format returns None."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            path = f.name
        try:
            df = self.handler.read_file(path)
            self.assertIsNone(df)
        finally:
            os.unlink(path)

    def test_read_file_from_bytes_csv(self):
        """Test reading CSV from bytes."""
        csv_bytes = b"a,b,c\n1,2,3\n4,5,6\n"
        df = self.handler.read_file_from_bytes(csv_bytes, "test.csv")
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 2)
        self.assertEqual(list(df.columns), ['a', 'b', 'c'])

    def test_read_file_from_bytes_excel(self):
        """Test reading Excel from bytes."""
        df_src = pd.DataFrame({'x': [1, 2], 'y': [3, 4]})
        buffer = io.BytesIO()
        df_src.to_excel(buffer, index=False)
        buffer.seek(0)
        df = self.handler.read_file_from_bytes(buffer.getvalue(), "test.xlsx")
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 2)

    def test_read_file_from_bytes_unsupported(self):
        """Test reading unsupported format from bytes returns None."""
        df = self.handler.read_file_from_bytes(b"content", "test.txt")
        self.assertIsNone(df)

    def test_supported_formats(self):
        """Test supported formats are defined."""
        self.assertIn('csv', self.handler.supported_formats)
        self.assertIn('xlsx', self.handler.supported_formats)
        self.assertIn('xls', self.handler.supported_formats)


if __name__ == '__main__':
    unittest.main()
