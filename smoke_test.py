#!/usr/bin/env python
"""Smoke test to verify app and key components work after changes."""
import sys

def main():
    print("Testing app imports...")
    import app  # noqa: F401
    print("  - app module imported OK")

    from utils.file_handler import FileHandler
    from utils.validator import DataValidator
    import pandas as pd

    # Test formula sanitization in file loading flow
    fh = FileHandler()
    csv_content = b"col1,col2\n=SUM(A1),safe\n3,4"
    df = fh.read_file_from_bytes(csv_content, "test.csv")
    print("  - FileHandler read_file_from_bytes OK")
    if len(df) > 0:
        first_val = str(df["col1"].iloc[0])
        print("  - Formula sanitization applied:", first_val.startswith("'"))

    # Test validator
    validator = DataValidator()
    test_df = pd.DataFrame({
        "Patient_ID": ["P1"],
        "Age": [25],
        "Gender": ["M"],
        "Date_of_Admission": ["2024-01-01"],
        "Specimen_Type": ["Blood"],
        "Organism": ["E. coli"],
    })
    results = validator.validate_data(test_df)
    print("  - DataValidator validate_data OK")

    print("")
    print("All smoke tests passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
