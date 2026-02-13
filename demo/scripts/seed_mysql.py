#!/usr/bin/env python3
"""Seed the MySQL demo database with schema and data."""

import os
import sys
from typing import List

import pymysql


def _split_statements(sql: str) -> List[str]:
    return [stmt.strip() for stmt in sql.split(";") if stmt.strip()]


def _read_file(path: str) -> str:
    with open(path, "r") as handle:
        return handle.read()


def main() -> int:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    schema_path = os.path.join(base_dir, "mysql", "schema.sql")
    seed_path = os.path.join(base_dir, "mysql", "seed.sql")

    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = int(os.getenv("DB_PORT", "3306"))
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")

    try:
        connection = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            autocommit=True,
        )
    except pymysql.MySQLError as exc:
        print(f"ERROR: Unable to connect to MySQL: {exc}")
        return 1

    try:
        with connection.cursor() as cursor:
            for statement in _split_statements(_read_file(schema_path)):
                cursor.execute(statement)
            for statement in _split_statements(_read_file(seed_path)):
                cursor.execute(statement)
    except pymysql.MySQLError as exc:
        print(f"ERROR: Failed to execute seed SQL: {exc}")
        return 1
    finally:
        connection.close()

    print("Seeded commercial_finance database successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
