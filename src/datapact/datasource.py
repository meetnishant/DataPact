"""
Data source loading and schema inference.
Handles loading CSV, Parquet, JSONL files and database sources.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Iterator, List
from pathlib import Path
import random
import sqlite3
import pandas as pd


def _infer_schema_from_df(df: pd.DataFrame) -> Dict[str, str]:
    schema: Dict[str, str] = {}
    for col in df.columns:
        dtype = str(df[col].dtype)
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


@dataclass
class DatabaseConfig:
    db_type: str
    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    table: Optional[str] = None
    query: Optional[str] = None
    path: Optional[str] = None
    connect_timeout: int = 10


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
                return (
                    pd.concat(samples, ignore_index=True) if samples else pd.DataFrame()
                )

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
        return _infer_schema_from_df(df)


class DatabaseSource:
    """
    Load and infer schema from database sources.
    """

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.df: Optional[pd.DataFrame] = None

    def _build_query(self) -> str:
        if self.config.query:
            return self.config.query
        if self.config.table:
            return f"SELECT * FROM {self.config.table}"
        raise ValueError("Database source requires --db-table or --db-query")

    def _connect(self):
        db_type = self.config.db_type
        if db_type == "sqlite":
            if not self.config.path:
                raise ValueError("SQLite requires --db-path")
            return sqlite3.connect(
                self.config.path,
                timeout=self.config.connect_timeout,
            )
        if db_type == "postgres":
            try:
                import psycopg2
            except ImportError as exc:
                raise ImportError(
                    "psycopg2-binary is required for Postgres support"
                ) from exc
            return psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                dbname=self.config.name,
                connect_timeout=self.config.connect_timeout,
            )
        if db_type == "mysql":
            try:
                import pymysql
            except ImportError as exc:
                raise ImportError("pymysql is required for MySQL support") from exc
            return pymysql.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                database=self.config.name,
                connect_timeout=self.config.connect_timeout,
            )
        raise ValueError(f"Unsupported db_type '{db_type}'")

    def load(self) -> pd.DataFrame:
        if self.df is not None:
            return self.df

        query = self._build_query()
        conn = self._connect()
        try:
            self.df = pd.read_sql_query(query, conn)
        finally:
            conn.close()

        return self.df

    def iter_chunks(self, chunksize: int) -> Iterator[pd.DataFrame]:
        query = self._build_query()
        conn = self._connect()
        try:
            for chunk in pd.read_sql_query(query, conn, chunksize=chunksize):
                yield chunk
        finally:
            conn.close()

    def sample_dataframe(
        self,
        sample_rows: Optional[int] = None,
        sample_frac: Optional[float] = None,
        seed: Optional[int] = None,
        chunksize: int = 10000,
    ) -> pd.DataFrame:
        if sample_rows is not None and sample_frac is not None:
            raise ValueError("Specify only one of sample_rows or sample_frac")

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

        return self.load()

    def infer_schema(self) -> Dict[str, str]:
        df = self.load()
        return _infer_schema_from_df(df)
