"""
Data source loading and schema inference.
Handles loading CSV, Parquet, JSONL files and inferring schema for contract generation.
"""

from typing import Optional, Dict, Iterator, List
from pathlib import Path
import random
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

    def iter_chunks(self, chunksize: int) -> Iterator[pd.DataFrame]:
        """
        Stream data in chunks for supported formats.
        """
        if self.format == "csv":
            return pd.read_csv(self.filepath, chunksize=chunksize)
        if self.format == "jsonl":
            return pd.read_json(self.filepath, lines=True, chunksize=chunksize)
        raise ValueError("Chunked loading is supported for CSV and JSONL only")

    def sample_dataframe(
        self,
        sample_rows: Optional[int] = None,
        sample_frac: Optional[float] = None,
        seed: Optional[int] = None,
        chunksize: int = 10000,
    ) -> pd.DataFrame:
        """
        Sample rows from the data source for large datasets.
        """
        if sample_rows is not None and sample_frac is not None:
            raise ValueError("Specify only one of sample_rows or sample_frac")

        if self.format in {"csv", "jsonl"}:
            if sample_frac is not None:
                samples: List[pd.DataFrame] = []
                for chunk in self.iter_chunks(chunksize):
                    if len(chunk) == 0:
                        continue
                    samples.append(chunk.sample(frac=sample_frac, random_state=seed))
                return pd.concat(samples, ignore_index=True) if samples else pd.DataFrame()

            if sample_rows is not None:
                rng = random.Random(seed)
                reservoir: List[dict] = []
                seen = 0
                for chunk in self.iter_chunks(chunksize):
                    records = chunk.to_dict("records")
                    for record in records:
                        seen += 1
                        if len(reservoir) < sample_rows:
                            reservoir.append(record)
                            continue
                        target = rng.randint(1, seen)
                        if target <= sample_rows:
                            reservoir[target - 1] = record
                return pd.DataFrame(reservoir)

        df = self.load()
        if sample_frac is not None:
            return df.sample(frac=sample_frac, random_state=seed)
        if sample_rows is not None:
            return df.sample(n=min(sample_rows, len(df)), random_state=seed)
        return df

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
