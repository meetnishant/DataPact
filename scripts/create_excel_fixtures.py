#!/usr/bin/env python3
"""
Script to create Excel test fixtures from existing CSV files.
"""

import pandas as pd
from pathlib import Path

# Base directory for fixtures
fixtures_dir = Path(__file__).parent.parent / "tests" / "fixtures"

# CSV files to convert to Excel
csv_files_to_convert = [
    "valid_customers.csv",
    "invalid_customers.csv",
    "quality_nulls.csv",
    "quality_valid.csv",
    "schema_valid.csv",
    "schema_missing_required.csv",
    "schema_type_mismatch.csv",
    "quality_enum_fail.csv",
    "quality_regex_fail.csv",
    "quality_minmax_fail.csv",
]

def create_excel_fixtures():
    """Convert CSV fixtures to Excel format."""
    for csv_file in csv_files_to_convert:
        csv_path = fixtures_dir / csv_file
        if not csv_path.exists():
            print(f"Skipping {csv_file} (not found)")
            continue
        
        # Read CSV
        df = pd.read_csv(csv_path)
        
        # Create Excel filename
        xlsx_file = csv_file.replace(".csv", ".xlsx")
        xlsx_path = fixtures_dir / xlsx_file
        
        # Write to Excel
        df.to_excel(xlsx_path, sheet_name="data", index=False)
        print(f"✓ Created {xlsx_file}")

if __name__ == "__main__":
    create_excel_fixtures()
    print("\nExcel fixtures created successfully!")
