"""Contract provider tests."""

from pathlib import Path

import pytest
import yaml

from datapact.cli import _resolve_contract_provider
from datapact.contracts import Contract
from datapact.providers.datapact_provider import DataPactProvider
from datapact.providers.odcs_provider import OdcsProvider
from datapact.providers.pact_provider import PactProvider


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load_yaml(path: Path):
    return yaml.safe_load(path.read_text())


def test_datapact_provider_can_load_datapact_contract() -> None:
    provider = DataPactProvider()
    data = _load_yaml(FIXTURES_DIR / "customer_contract.yaml")

    assert provider.can_load(data) is True


def test_datapact_provider_rejects_odcs_contract() -> None:
    provider = DataPactProvider()
    data = _load_yaml(FIXTURES_DIR / "odcs_minimal.yaml")

    assert provider.can_load(data) is False


def test_datapact_provider_loads_from_dict() -> None:
    provider = DataPactProvider()
    data = _load_yaml(FIXTURES_DIR / "customer_contract.yaml")

    contract = provider.load_from_dict(data)

    assert contract.name == "customer_data"
    assert contract.dataset.name == "customers"
    assert len(contract.fields) == 6


def test_datapact_provider_loads_from_path() -> None:
    provider = DataPactProvider()
    path = FIXTURES_DIR / "customer_contract.yaml"

    contract = provider.load_from_path(str(path))

    assert contract.name == "customer_data"
    assert contract.version == "2.0.0"


def test_odcs_provider_can_load_odcs_contract() -> None:
    provider = OdcsProvider()
    data = _load_yaml(FIXTURES_DIR / "odcs_minimal.yaml")

    assert provider.can_load(data) is True


def test_odcs_provider_loads_from_dict() -> None:
    provider = OdcsProvider()
    data = _load_yaml(FIXTURES_DIR / "odcs_minimal.yaml")

    contract = provider.load_from_dict(data)

    assert contract.dataset.name == "customers"
    assert contract.name == "odcs_customers"
    assert provider.odcs_warnings == []


def test_odcs_provider_rejects_invalid_version() -> None:
    provider = OdcsProvider()
    data = _load_yaml(FIXTURES_DIR / "odcs_invalid_version.yaml")

    try:
        provider.load_from_dict(data)
    except ValueError as exc:
        assert "Unsupported ODCS apiVersion" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid ODCS version")


def test_odcs_provider_loads_selected_object() -> None:
    provider = OdcsProvider(odcs_object="orders")
    data = _load_yaml(FIXTURES_DIR / "odcs_multi_object.yaml")

    contract = provider.load_from_dict(data)

    assert contract.dataset.name == "orders"
    assert {field.name for field in contract.fields} == {"order_id", "amount"}


def test_cli_resolves_datapact_provider() -> None:
    data = _load_yaml(FIXTURES_DIR / "customer_contract.yaml")

    provider = _resolve_contract_provider("datapact", data, None)

    assert provider.name == "datapact"


def test_cli_resolves_odcs_provider() -> None:
    data = _load_yaml(FIXTURES_DIR / "odcs_minimal.yaml")

    provider = _resolve_contract_provider("odcs", data, None)

    assert provider.name == "odcs"


def test_cli_auto_selects_odcs_provider() -> None:
    data = _load_yaml(FIXTURES_DIR / "odcs_minimal.yaml")

    provider = _resolve_contract_provider("auto", data, None)

    assert provider.name == "odcs"


def test_cli_rejects_mismatched_format() -> None:
    data = _load_yaml(FIXTURES_DIR / "customer_contract.yaml")

    with pytest.raises(ValueError, match="does not match"):
        _resolve_contract_provider("odcs", data, None)


def test_contract_parses_flatten_config() -> None:
    data = {
        "contract": {"name": "flatten_test", "version": "2.0.0"},
        "dataset": {"name": "customers"},
        "flatten": {"enabled": True, "separator": "__"},
        "fields": [
            {"name": "id", "type": "integer"},
        ],
    }

    contract = Contract._from_dict(data)

    assert contract.flatten.enabled is True
    assert contract.flatten.separator == "__"


def test_pact_provider_loads_pact_contract() -> None:
    provider = PactProvider()
    path = FIXTURES_DIR / "pact_user_api.json"

    contract = provider.load(str(path))

    assert contract.name == "web_frontend_user_api"
    assert contract.dataset.name == "user-api-api"
    assert len(contract.fields) == 5  # id, name, email, age, active


def test_pact_provider_infers_field_types() -> None:
    provider = PactProvider()
    path = FIXTURES_DIR / "pact_user_api.json"

    contract = provider.load(str(path))

    # Verify type inference
    fields_by_name = {f.name: f for f in contract.fields}
    assert fields_by_name["id"].type == "integer"
    assert fields_by_name["name"].type == "string"
    assert fields_by_name["email"].type == "string"
    assert fields_by_name["age"].type == "integer"
    assert fields_by_name["active"].type == "boolean"


def test_pact_provider_marks_fields_as_optional() -> None:
    provider = PactProvider()
    path = FIXTURES_DIR / "pact_user_api.json"

    contract = provider.load(str(path))

    # Pact doesn't define required fields, so all should be optional
    for field in contract.fields:
        assert field.required is False


def test_pact_provider_rejects_missing_response_body() -> None:
    provider = PactProvider()
    data = {
        "consumer": {"name": "test-consumer"},
        "provider": {"name": "test-provider"},
        "interactions": [
            {
                "description": "a request",
                "response": {
                    "status": 200,
                    "body": None,  # Invalid: no body
                },
            }
        ],
    }

    with pytest.raises(ValueError, match="response body must be a JSON object"):
        provider._from_pact_dict(data, "test.json")


def test_pact_provider_rejects_non_object_response_body() -> None:
    provider = PactProvider()
    data = {
        "consumer": {"name": "test-consumer"},
        "provider": {"name": "test-provider"},
        "interactions": [
            {
                "description": "a request",
                "response": {
                    "status": 200,
                    "body": [{"id": 1}],  # Invalid: array instead of object
                },
            }
        ],
    }

    with pytest.raises(ValueError, match="response body must be a JSON object"):
        provider._from_pact_dict(data, "test.json")
