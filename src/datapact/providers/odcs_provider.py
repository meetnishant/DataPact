"""Provider for ODCS contracts."""

from typing import Any, Dict, List, Optional

from datapact.contracts import Contract
from datapact.odcs_contracts import OdcsContract, is_odcs_contract
from datapact.providers.base import ContractProvider
from datapact.versioning import check_odcs_compatibility


class OdcsProvider(ContractProvider):
    """Load ODCS contracts and map them to DataPact contracts."""

    name = "odcs"

    def __init__(self, odcs_object: Optional[str] = None) -> None:
        self.odcs_object = odcs_object
        self.odcs_warnings: List[str] = []
        self.odcs_metadata: Optional[Dict[str, Any]] = None

    def can_load(self, data: Dict[str, Any]) -> bool:
        return is_odcs_contract(data)

    def load_from_dict(self, data: Dict[str, Any]) -> Contract:
        odcs_contract = OdcsContract.from_dict(data)
        is_compatible, message = check_odcs_compatibility(odcs_contract.api_version)
        if not is_compatible:
            raise ValueError(message)

        contract, warnings, metadata = odcs_contract.to_datapact_contract(
            self.odcs_object
        )
        self.odcs_warnings = warnings
        self.odcs_metadata = metadata
        return contract
