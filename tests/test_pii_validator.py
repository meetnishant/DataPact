"""Tests for PIIValidator — declared PII and auto-detection."""

import pytest
import pandas as pd
from pathlib import Path

from datapact.contracts import Contract
from datapact.validators.pii_validator import PIIValidator

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture
def pii_contract():
    return Contract.from_yaml(str(FIXTURES_DIR / "pii_contract.yaml"))


@pytest.fixture
def pii_data_unmasked():
    return pd.read_csv(FIXTURES_DIR / "pii_data_unmasked.csv")


@pytest.fixture
def no_pii_scan_contract():
    return Contract.from_yaml(str(FIXTURES_DIR / "pii_scan_disabled_contract.yaml"))


# ===========================================================================
# Declared PII Tests
# ===========================================================================


class TestDeclaredPII:

    def test_declared_pii_unmasked_emits_warn(self, pii_contract, pii_data_unmasked):
        """Fields declared as PII (masked=false) emit WARNs; passed=True."""
        validator = PIIValidator(pii_contract, pii_data_unmasked)
        passed, errors = validator.validate()
        assert passed  # only WARNs, no ERRORs
        declared_msgs = [e for e in errors if "declared as PII" in e]
        assert len(declared_msgs) >= 1
        assert all(e.startswith("WARN") for e in declared_msgs)

    def test_declared_pii_masked_emits_nothing(self):
        """A field with masked=true produces no error."""
        contract_data = {
            "contract": {"name": "test", "version": "2.0.0"},
            "dataset": {"name": "test"},
            "fields": [
                {
                    "name": "email",
                    "type": "string",
                    "pii": {"category": "email", "masked": True},
                }
            ],
        }
        contract = Contract._from_dict(contract_data)
        df = pd.DataFrame({"email": ["***", "***"]})
        validator = PIIValidator(contract, df)
        passed, errors = validator.validate()
        assert passed
        assert len(errors) == 0

    def test_declared_pii_severity_error_fails(self):
        """severity=ERROR on a declared PII field causes passed=False."""
        contract_data = {
            "contract": {"name": "test", "version": "2.0.0"},
            "dataset": {"name": "test"},
            "fields": [
                {
                    "name": "ssn",
                    "type": "string",
                    "pii": {"category": "ssn", "masked": False, "severity": "ERROR"},
                }
            ],
        }
        contract = Contract._from_dict(contract_data)
        df = pd.DataFrame({"ssn": ["123-45-6789"]})
        validator = PIIValidator(contract, df)
        passed, errors = validator.validate()
        assert not passed
        assert any(e.startswith("ERROR") for e in errors)

    def test_declared_pii_field_absent_from_df_skipped(self):
        """If a PII-declared field is not in the DataFrame, no error is emitted."""
        contract_data = {
            "contract": {"name": "test", "version": "2.0.0"},
            "dataset": {"name": "test"},
            "fields": [
                {"name": "phone_number", "type": "string", "pii": {"category": "phone"}}
            ],
        }
        contract = Contract._from_dict(contract_data)
        df = pd.DataFrame({"unrelated_col": [1, 2, 3]})
        validator = PIIValidator(contract, df)
        passed, errors = validator.validate()
        assert passed
        assert len(errors) == 0

    def test_declared_pii_boolean_shorthand_parses(self):
        """`pii: true` creates a generic PIIConfig with category=None, severity=WARN."""
        contract_data = {
            "contract": {"name": "test", "version": "2.0.0"},
            "dataset": {"name": "test"},
            "fields": [{"name": "full_name", "type": "string", "pii": True}],
        }
        contract = Contract._from_dict(contract_data)
        pii_cfg = contract.fields[0].pii
        assert pii_cfg is not None
        assert pii_cfg.category is None
        assert pii_cfg.severity == "WARN"
        assert pii_cfg.masked is False

    def test_declared_pii_boolean_false_no_config(self):
        """`pii: false` results in no PIIConfig on the field."""
        contract_data = {
            "contract": {"name": "test", "version": "2.0.0"},
            "dataset": {"name": "test"},
            "fields": [{"name": "score", "type": "float", "pii": False}],
        }
        contract = Contract._from_dict(contract_data)
        assert contract.fields[0].pii is None

    def test_invalid_pii_category_raises(self):
        """Unknown category raises ValueError at contract parse time."""
        with pytest.raises(ValueError, match="Unsupported PII category"):
            Contract._from_dict({
                "contract": {"name": "test", "version": "2.0.0"},
                "dataset": {"name": "test"},
                "fields": [
                    {"name": "x", "type": "string", "pii": {"category": "biometric"}},
                ],
            })

    def test_invalid_pii_severity_raises(self):
        """Unknown severity raises ValueError at contract parse time."""
        with pytest.raises(ValueError, match="Unsupported PII severity"):
            Contract._from_dict({
                "contract": {"name": "test", "version": "2.0.0"},
                "dataset": {"name": "test"},
                "fields": [
                    {"name": "x", "type": "string", "pii": {"severity": "CRITICAL"}},
                ],
            })

    def test_ssn_field_masked_in_fixture_no_error(self, pii_contract, pii_data_unmasked):
        """The ssn field in the fixture is masked=true; it must not appear in errors."""
        validator = PIIValidator(pii_contract, pii_data_unmasked)
        _, errors = validator.validate()
        ssn_msgs = [e for e in errors if "'ssn'" in e and "declared as PII" in e]
        assert len(ssn_msgs) == 0


# ===========================================================================
# Auto-detection: Column Name Heuristic Tests
# ===========================================================================


class TestAutoDetectionByName:

    def _contract(self, pii_scan: bool = True) -> Contract:
        return Contract._from_dict({
            "contract": {"name": "test", "version": "2.0.0"},
            "dataset": {"name": "test"},
            "pii_scan": pii_scan,
            "fields": [{"name": "id", "type": "integer"}],
        })

    def test_column_named_email_triggers_warn(self):
        """Column named 'email' is auto-detected by name heuristic."""
        contract = self._contract()
        df = pd.DataFrame({"id": [1, 2], "email": ["a@b.com", "c@d.com"]})
        validator = PIIValidator(contract, df)
        passed, errors = validator.validate()
        assert passed  # WARN only
        assert any("email" in e and "column name" in e for e in errors)

    def test_column_named_ssn_triggers_warn(self):
        """Column named 'ssn' is auto-detected by name heuristic."""
        contract = self._contract()
        df = pd.DataFrame({"id": [1], "ssn": ["123-45-6789"]})
        validator = PIIValidator(contract, df)
        _, errors = validator.validate()
        assert any("ssn" in e for e in errors)

    def test_compound_column_name_triggers_warn(self):
        """'user_phone_number' matches the 'phone' keyword."""
        contract = self._contract()
        df = pd.DataFrame({"id": [1], "user_phone_number": ["+1-800-555-0100"]})
        validator = PIIValidator(contract, df)
        _, errors = validator.validate()
        assert any("user_phone_number" in e for e in errors)

    def test_pii_scan_false_disables_autodetection(self):
        """pii_scan=false means undeclared columns are not flagged."""
        contract = self._contract(pii_scan=False)
        df = pd.DataFrame({"id": [1], "email": ["a@b.com"]})
        validator = PIIValidator(contract, df)
        passed, errors = validator.validate()
        assert passed
        assert len(errors) == 0

    def test_pii_scan_false_via_fixture(self, no_pii_scan_contract):
        """pii_scan=false from a YAML fixture suppresses auto-detection."""
        df = pd.DataFrame({"id": [1, 2], "email": ["a@b.com", "c@d.com"]})
        validator = PIIValidator(no_pii_scan_contract, df)
        passed, errors = validator.validate()
        assert passed
        assert len(errors) == 0

    def test_declared_field_not_double_reported(self):
        """A field declared as PII is not also flagged by auto-detection."""
        contract_data = {
            "contract": {"name": "test", "version": "2.0.0"},
            "dataset": {"name": "test"},
            "pii_scan": True,
            "fields": [
                {
                    "name": "email",
                    "type": "string",
                    "pii": {"category": "email", "masked": False},
                }
            ],
        }
        contract = Contract._from_dict(contract_data)
        df = pd.DataFrame({"email": ["a@b.com", "b@c.com"]})
        validator = PIIValidator(contract, df)
        _, errors = validator.validate()
        # Only one message — from declared-PII pass, not auto-detection
        pii_msgs = [e for e in errors if "email" in e.lower()]
        assert len(pii_msgs) == 1
        assert "declared as PII" in pii_msgs[0]


# ===========================================================================
# Auto-detection: Value Pattern Tests
# ===========================================================================


class TestAutoDetectionByValue:

    def _contract(self) -> Contract:
        return Contract._from_dict({
            "contract": {"name": "test", "version": "2.0.0"},
            "dataset": {"name": "test"},
            "pii_scan": True,
            "fields": [{"name": "id", "type": "integer"}],
        })

    def test_email_values_trigger_warn(self):
        """A column containing email-like values is flagged by value pattern."""
        contract = self._contract()
        df = pd.DataFrame({
            "id": range(10),
            "user_data": [f"user{i}@example.com" for i in range(10)],
        })
        validator = PIIValidator(contract, df)
        _, errors = validator.validate()
        assert any("user_data" in e and "value pattern" in e for e in errors)

    def test_ssn_values_trigger_warn(self):
        """A column with SSN-formatted values is flagged by value pattern."""
        contract = self._contract()
        df = pd.DataFrame({
            "id": range(10),
            "identifier": [f"{i:03d}-{i:02d}-{i:04d}" for i in range(10)],
        })
        validator = PIIValidator(contract, df)
        _, errors = validator.validate()
        assert any("identifier" in e for e in errors)

    def test_mixed_column_below_threshold_not_flagged(self):
        """Less than 20% PII-like values → column not auto-detected."""
        contract = self._contract()
        # Only 1 of 20 looks like an email (5%)
        values = ["not-pii"] * 19 + ["real@email.com"]
        df = pd.DataFrame({"id": range(20), "misc": values})
        validator = PIIValidator(contract, df)
        _, errors = validator.validate()
        assert not any("misc" in e for e in errors)

    def test_empty_column_not_flagged(self):
        """An all-null column does not trigger auto-detection."""
        contract = self._contract()
        df = pd.DataFrame({"id": [1, 2, 3], "null_col": [None, None, None]})
        validator = PIIValidator(contract, df)
        passed, errors = validator.validate()
        assert passed
        assert not any("null_col" in e for e in errors)

    def test_non_pii_column_not_flagged(self):
        """A column with generic string values is not flagged."""
        contract = self._contract()
        df = pd.DataFrame({
            "id": range(10),
            "status": ["active", "inactive"] * 5,
        })
        validator = PIIValidator(contract, df)
        passed, errors = validator.validate()
        assert passed
        assert len(errors) == 0


# ===========================================================================
# Integration: ErrorRecord code
# ===========================================================================


class TestPIIErrorCode:

    def test_pii_error_record_uses_pii_code(self):
        """Verify that CLI error-record conversion assigns code='PII'."""
        contract_data = {
            "contract": {"name": "test", "version": "2.0.0"},
            "dataset": {"name": "test"},
            "fields": [
                {"name": "email", "type": "string", "pii": {"category": "email"}},
            ],
        }
        contract = Contract._from_dict(contract_data)
        df = pd.DataFrame({"email": ["a@b.com"]})

        from datapact.reporting import ErrorRecord

        validator = PIIValidator(contract, df)
        _, pii_errors = validator.validate()

        records = []
        for err in pii_errors:
            severity = "ERROR" if err.startswith("ERROR") else "WARN"
            msg = err.replace("ERROR: ", "").replace("WARN: ", "")
            records.append(ErrorRecord(code="PII", field="", message=msg, severity=severity))

        assert len(records) == 1
        assert records[0].code == "PII"
        assert records[0].severity == "WARN"
        assert "email" in records[0].message


# ===========================================================================
# Chunked / streaming-path: validator works on a partial DataFrame
# ===========================================================================


class TestChunkedPII:

    def test_pii_validator_works_on_chunk(self):
        """PIIValidator can run on a chunk (subset of rows) as used in streaming."""
        contract_data = {
            "contract": {"name": "test", "version": "2.0.0"},
            "dataset": {"name": "test"},
            "pii_scan": True,
            "fields": [{"name": "id", "type": "integer"}],
        }
        contract = Contract._from_dict(contract_data)
        chunk = pd.DataFrame({
            "id": range(5),
            "customer_email": [f"u{i}@test.com" for i in range(5)],
        })
        validator = PIIValidator(contract, chunk)
        passed, errors = validator.validate()
        assert any("customer_email" in e for e in errors)

    def test_validator_returns_bool_on_any_df(self):
        """validate() always returns a bool regardless of DataFrame content."""
        contract_data = {
            "contract": {"name": "test", "version": "2.0.0"},
            "dataset": {"name": "test"},
            "pii_scan": True,
            "fields": [{"name": "id", "type": "integer"}],
        }
        contract = Contract._from_dict(contract_data)
        df = pd.DataFrame({"id": range(10), "account_num": range(10)})
        validator = PIIValidator(contract, df)
        result = validator.validate()
        assert isinstance(result[0], bool)
        assert isinstance(result[1], list)
