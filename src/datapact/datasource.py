"""
Data source loading and schema inference.
Handles loading CSV, Parquet, JSONL files and inferring schema for contract generation.
"""

from typing import Optional, Dict
from pathlib import Path
import pandas as pd


class DataSource:
    """
    Load and infer schema from various data formats (CSV, Parquet, JSONL).
    Provides methods for loading data and inferring contract field types.
    """

    def __init__(self, filepath: str, format: Optional[str] = None):
        """
        Initialize datasource.
        Args:
            filepath: Path to data file (CSV, Parquet, JSON)
            format: Data format ('csv', 'parquet', 'jsonl'). Auto-detected if None.
        """
        self.filepath = Path(filepath)
        self.format = format or self._detect_format()
        self.df: Optional[pd.DataFrame] = None

    def _detect_format(self) -> str:
        """
        Auto-detect data format from file extension.
        Returns 'csv', 'parquet', or 'jsonl'.
        """
        suffix = self.filepath.suffix.lower()
        format_map = {
            ".csv": "csv",
            ".parquet": "parquet",
            ".pq": "parquet",
            ".jsonl": "jsonl",
            ".ndjson": "jsonl",
        }
        return format_map.get(suffix, "csv")

    def load(self) -> pd.DataFrame:
        """
        Load data into a pandas DataFrame based on detected or specified format.
        Caches the DataFrame after first load.
        """
        # Return cached DataFrame to avoid re-reading the file
        if self.df is not None:
            return self.df

        if self.format == "csv":
            self.df = pd.read_csv(self.filepath)
        elif self.format == "parquet":
            self.df = pd.read_parquet(self.filepath)
        elif self.format == "jsonl":
            self.df = pd.read_json(self.filepath, lines=True)
        else:
            raise ValueError(f"Unsupported format: {self.format}")

        return self.df

    def infer_schema(self) -> Dict[str, str]:
        """
        Infer column names and types from the loaded DataFrame.
        Maps pandas dtypes to contract types (integer, float, string, boolean).
        """
        df = self.load()
        schema = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            # Map pandas dtypes to contract types
            if dtype.startswith("int"):
                schema[col] = "integer"
            elif dtype.startswith("float"):
                schema[col] = "float"
            elif dtype == "object" or dtype.startswith("string"):
                schema[col] = "string"
            elif dtype == "bool":
                schema[col] = "boolean"
            else:
                schema[col] = "string"
        return schema
