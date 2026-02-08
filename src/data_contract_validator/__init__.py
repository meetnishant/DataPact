"""Data Contract Validator - Framework for validating datasets against contracts."""

__version__ = "0.1.0"
__author__ = "Your Name"

from data_contract_validator.contracts import Contract
from data_contract_validator.reporting import ValidationReport
from data_contract_validator.datasource import DataSource

__all__ = ["Contract", "ValidationReport", "DataSource"]
