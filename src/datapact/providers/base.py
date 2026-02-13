"""Provider interface for loading contracts from different formats."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict

import yaml

from datapact.contracts import Contract


class ContractProvider(ABC):
    """Base interface for contract providers."""

    name: str

    @abstractmethod
    def can_load(self, data: Dict[str, Any]) -> bool:
        """Return True if the provider can load the given contract data."""
        raise NotImplementedError

    @abstractmethod
    def load_from_dict(self, data: Dict[str, Any]) -> Contract:
        """Parse a contract from a dictionary."""
        raise NotImplementedError

    def load_from_path(self, path: str) -> Contract:
        """Read a YAML contract file and parse it into a Contract."""
        data = yaml.safe_load(Path(path).read_text())
        return self.load_from_dict(data)
