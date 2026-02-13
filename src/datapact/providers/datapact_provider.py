"""Provider for native DataPact YAML contracts."""

from typing import Any, Dict

from datapact.contracts import Contract
from datapact.odcs_contracts import is_odcs_contract
from datapact.providers.base import ContractProvider


class DataPactProvider(ContractProvider):
    """Load DataPact-native YAML contracts."""

    name = "datapact"

    def can_load(self, data: Dict[str, Any]) -> bool:
        if not isinstance(data, dict):
            return False
        if is_odcs_contract(data):
            return False
        return "contract" in data and "fields" in data

    def load_from_dict(self, data: Dict[str, Any]) -> Contract:
        return Contract._from_dict(data)
