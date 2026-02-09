#!/usr/bin/env python
"""Setup file for DataPact."""

from setuptools import setup, find_packages

# Minimal setup.py for legacy tooling; pyproject.toml is authoritative.
setup(
    name="datapact",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)
