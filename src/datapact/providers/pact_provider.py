"""API Pact contract provider for DataPact integration."""

from typing import Any, Dict, List
import json

from datapact.providers.base import ContractProvider
from datapact.contracts import Contract, Field, Dataset


class PactProvider(ContractProvider):
    """
    Provider for converting API Pact contracts to DataPact contracts.

    Maps Pact interactions' response bodies to DataPact field schemas.
    Limitations:
    - Quality rules (not_null, unique, etc.) are NOT inferred from Pact.
    - Distribution rules are NOT supported.
    - Custom rules are NOT supported.
    - Warnings are logged for these unsupported features.
    """

    name = "pact"
    supports_format = "pact"

    def can_load(self, data: Dict[str, Any]) -> bool:
        """
        Check if data is a valid Pact contract.

        Pact contracts have consumer, provider, interactions, and metadata fields.
        """
        return (
            isinstance(data, dict)
            and "consumer" in data
            and "provider" in data
            and "interactions" in data
            and isinstance(data.get("interactions"), list)
        )

    def load_from_dict(self, data: Dict[str, Any]) -> Contract:
        """
        Parse a Pact dict to a DataPact contract.

        Note: Pact contracts are typically JSON files, not YAML.
        This method is provided for interface compliance.
        """
        return self._from_pact_dict(data, "pact_contract")

    @classmethod
    def load(cls, path: str) -> Contract:
        """
        Load and convert a Pact JSON file to a DataPact contract.

        Args:
            path: Path to Pact JSON file.

        Returns:
            Contract with fields inferred from Pact response body schema.

        Raises:
            ValueError: If Pact file is invalid or has no interactions.
        """
        with open(path, "r") as f:
            data = json.load(f)

        return cls._from_pact_dict(data, path)

    @classmethod
    def _from_pact_dict(cls, data: Dict[str, Any], path: str) -> Contract:
        """
        Convert Pact dict to DataPact contract.
        """
        if not isinstance(data, dict):
            raise ValueError("Pact file must contain a JSON object")

        consumer = data.get("consumer", {})
        provider = data.get("provider", {})
        interactions = data.get("interactions", [])

        if not interactions:
            raise ValueError(
                "Pact file must have at least one interaction with a response"
            )

        # Use first interaction's response body to infer fields
        first_interaction = interactions[0]
        response = first_interaction.get("response", {})
        body = response.get("body")

        if body is None or not isinstance(body, dict):
            raise ValueError(
                "Pact interaction response body must be a JSON object "
                f"(got {type(body).__name__})"
            )

        consumer_name = consumer.get("name", "pact-consumer")
        provider_name = provider.get("name", "pact-provider")
        contract_name = f"{consumer_name}_{provider_name}".replace("-", "_")

        # Infer fields from response body
        fields = cls._infer_fields_from_body(body)

        # Log warnings for unsupported Pact features
        cls._log_pact_limitations()

        return Contract(
            name=contract_name,
            version="2.0.0",
            dataset=Dataset(name=f"{provider_name}-api"),
            fields=fields,
        )

    @staticmethod
    def _infer_fields_from_body(body: Dict[str, Any]) -> List[Field]:
        """
        Infer DataPact fields from a JSON object structure.

        Maps JSON types to DataPact types:
        - int → integer
        - float → float
        - str → string
        - bool → boolean
        - All fields are non-required by default (Pact doesn't enforce this).
        """
        fields: List[Field] = []

        for key, value in body.items():
            field_type = PactProvider._infer_type(value)
            fields.append(
                Field(
                    name=key,
                    type=field_type,
                    required=False,  # Pact doesn't enforce required fields
                    rules=None,
                    distribution=None,
                )
            )

        return fields

    @staticmethod
    def _infer_type(value: Any) -> str:
        """Infer DataPact field type from JSON value."""
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "string"
        elif value is None:
            return "string"  # Default to string for null
        else:
            return "string"  # Fallback for complex types

    @staticmethod
    def _log_pact_limitations() -> None:
        """Log warnings about unsupported Pact features in DataPact."""
        print(
            "WARN: Pact provider: quality rules (not_null, unique, etc.) "
            "are NOT inferred from Pact contracts."
        )
        print(
            "WARN: Pact provider: distribution rules (mean, std, drift) "
            "are NOT supported."
        )
        print(
            "WARN: Pact provider: custom rules are NOT supported. "
            "Add them manually to the DataPact contract if needed."
        )
