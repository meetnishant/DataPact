"""
Data Contract Validator - Framework for validating datasets against contracts.
Exposes core classes for contract, reporting, and data loading.
"""

# Package metadata used by tooling and reports
__version__ = "0.1.0"
__author__ = "Your Name"

# Public API re-exports for convenience
from data_contract_validator.contracts import Contract
from data_contract_validator.reporting import ValidationReport
from data_contract_validator.datasource import DataSource

__all__ = ["Contract", "ValidationReport", "DataSource"]
