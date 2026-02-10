"""Tests for database data sources."""

from pathlib import Path
import os
import sqlite3

import pytest

from datapact.datasource import DatabaseConfig, DatabaseSource


def _create_sqlite_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "sample.db"
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE customers (id INTEGER, email TEXT, age INTEGER)"
        )
        cursor.executemany(
            "INSERT INTO customers (id, email, age) VALUES (?, ?, ?)",
            [
                (1, "a@example.com", 30),
                (2, "b@example.com", 25),
                (3, "c@example.com", 40),
            ],
        )
        conn.commit()
    finally:
        conn.close()
    return db_path


def test_sqlite_load_and_infer_schema(tmp_path: Path) -> None:
    db_path = _create_sqlite_db(tmp_path)
    config = DatabaseConfig(
        db_type="sqlite",
        path=str(db_path),
        table="customers",
    )
    ds = DatabaseSource(config)
    df = ds.load()

    assert len(df) == 3
    assert set(df.columns) == {"id", "email", "age"}

    schema = ds.infer_schema()
    assert schema["id"] == "integer"
    assert schema["email"] == "string"


def test_sqlite_iter_chunks(tmp_path: Path) -> None:
    db_path = _create_sqlite_db(tmp_path)
    config = DatabaseConfig(
        db_type="sqlite",
        path=str(db_path),
        table="customers",
    )
    ds = DatabaseSource(config)
    chunks = list(ds.iter_chunks(chunksize=2))

    assert [len(chunk) for chunk in chunks] == [2, 1]


def test_missing_table_or_query_raises() -> None:
    config = DatabaseConfig(db_type="sqlite", path=":memory:")
    ds = DatabaseSource(config)

    with pytest.raises(ValueError):
        _ = ds.load()


def test_mysql_load_table() -> None:
    if os.getenv("DATAPACT_MYSQL_TESTS") != "1":
        pytest.skip("MySQL tests disabled; set DATAPACT_MYSQL_TESTS=1")

    pytest.importorskip("pymysql")

    password = os.getenv("DATAPACT_MYSQL_PASSWORD")
    if not password:
        pytest.skip("MySQL password not set; set DATAPACT_MYSQL_PASSWORD")

    config = DatabaseConfig(
        db_type="mysql",
        host=os.getenv("DATAPACT_MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("DATAPACT_MYSQL_PORT", "3306")),
        user=os.getenv("DATAPACT_MYSQL_USER", "root"),
        password=password,
        name=os.getenv("DATAPACT_MYSQL_DB", "datapact_test"),
        table=os.getenv("DATAPACT_MYSQL_TABLE", "customers"),
    )

    ds = DatabaseSource(config)
    df = ds.load()

    assert len(df) >= 3
    assert {"id", "email", "age"}.issubset(set(df.columns))
