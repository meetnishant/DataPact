"""ODCS contract parsing and mapping tests."""

from pathlib import Path

import pytest

from datapact.odcs_contracts import OdcsContract
from datapact.versioning import check_odcs_compatibility


def test_odcs_minimal_mapping() -> None:
    fixture = Path("tests/fixtures/odcs_minimal.yaml")
    data = fixture.read_text()

    odcs = OdcsContract.from_dict(_load_yaml(data))
    contract, warnings, _metadata = odcs.to_datapact_contract()

    assert contract.name == "odcs_customers"
    assert contract.dataset.name == "customers"
    assert len(contract.fields) == 3

    id_field = next(field for field in contract.fields if field.name == "id")
    email_field = next(field for field in contract.fields if field.name == "email")

    assert id_field.rules is not None
    assert id_field.rules.unique is True

    assert email_field.rules is not None
    assert email_field.rules.not_null is True

    assert contract.sla.min_rows == 100
    assert warnings == []


def test_odcs_requires_object_selection_when_multiple() -> None:
    fixture = Path("tests/fixtures/odcs_multi_object.yaml")
    odcs = OdcsContract.from_dict(_load_yaml(fixture.read_text()))

    with pytest.raises(ValueError, match="multiple schema objects"):
        _ = odcs.to_datapact_contract()

    contract, warnings, _metadata = odcs.to_datapact_contract("orders")

    assert contract.dataset.name == "orders"
    assert {field.name for field in contract.fields} == {"order_id", "amount"}
    assert warnings == []


def test_odcs_invalid_version_rejected() -> None:
    fixture = Path("tests/fixtures/odcs_invalid_version.yaml")
    odcs = OdcsContract.from_dict(_load_yaml(fixture.read_text()))

    ok, message = check_odcs_compatibility(odcs.api_version)

    assert ok is False
    assert "Unsupported ODCS apiVersion" in message


def test_odcs_quality_sql_custom_warns() -> None:
    fixture = Path("tests/fixtures/odcs_quality_sql_custom.yaml")
    odcs = OdcsContract.from_dict(_load_yaml(fixture.read_text()))

    _contract, warnings, _metadata = odcs.to_datapact_contract()

    assert any("type 'sql'" in warning for warning in warnings)
    assert any("type 'custom'" in warning for warning in warnings)


def test_odcs_logical_type_timestamp_warns() -> None:
    fixture = Path("tests/fixtures/odcs_logical_type_timestamp.yaml")
    odcs = OdcsContract.from_dict(_load_yaml(fixture.read_text()))

    _contract, warnings, _metadata = odcs.to_datapact_contract()

    assert any("logicalType 'date'" in warning for warning in warnings)
    assert any("logicalType 'time'" in warning for warning in warnings)
    assert any("logicalType 'timestamp'" in warning for warning in warnings)


def _load_yaml(raw: str):
    import yaml

    return yaml.safe_load(raw)
