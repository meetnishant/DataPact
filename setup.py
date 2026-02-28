#!/usr/bin/env python
"""Setup file for DataPact."""

from setuptools import setup, find_packages

# Minimal setup.py for legacy tooling; pyproject.toml is authoritative.
setup(
    name="datapact",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "testcontainers[kafka]>=3.7.1",
            "ruff>=0.1.0",
            "black>=23.0",
            "mypy>=1.0",
        ],
        "db": [
            "psycopg2-binary>=2.9",
            "pymysql>=1.1",
        ],
        "streaming": [
            "confluent-kafka>=2.3.0",
        ],
        "flink": [
            "pyflink>=1.18.0",
        ],
        "spark": [
            "pyspark>=3.5.0",
        ],
    },
)
