#!/usr/bin/env python
"""Setup file for data-contract-validator."""

from setuptools import setup, find_packages

setup(
    name="data-contract-validator",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)
