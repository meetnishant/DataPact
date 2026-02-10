"""
DataPact - Framework for validating datasets against contracts.
Exposes core classes for contract, reporting, and data loading.
"""

# Package metadata used by tooling and reports
__version__ = "0.1.0"
__author__ = "Your Name"

# Public API re-exports for convenience
from datapact.contracts import Contract
from datapact.reporting import ValidationReport
from datapact.datasource import DataSource, DatabaseSource, DatabaseConfig
from datapact.profiling import profile_dataframe
from datapact.odcs_contracts import OdcsContract

__all__ = [
	"Contract",
	"ValidationReport",
	"DataSource",
	"DatabaseSource",
	"DatabaseConfig",
	"profile_dataframe",
	"OdcsContract",
]
