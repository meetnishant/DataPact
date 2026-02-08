#!/usr/bin/env python
"""Setup file for data-contract-validator."""

from setuptools import setup, find_packages

# Minimal setup.py for legacy tooling; pyproject.toml is authoritative.
setup(
    name="data-contract-validator",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)
