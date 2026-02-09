from pathlib import Path
import pandas as pd
import pytest

from datapact.contracts import Contract
from datapact.datasource import DataSource
from datapact.validators import (
    SchemaValidator,
    QualityValidator,
    DistributionValidator,
    SLAValidator,
    CustomRuleValidator,
)
from datapact.cli import _parse_severity_overrides, _parse_webhook_headers


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _contract(path: str) -> Contract:
    return Contract.from_yaml(str(FIXTURES_DIR / path))


def _df(path: str) -> pd.DataFrame:
    return pd.read_csv(FIXTURES_DIR / path)


class TestSchemaValidationExhaustive:
    def test_schema_valid(self):
        contract = _contract("schema_contract.yaml")
        df = _df("schema_valid.csv")
        passed, errors = SchemaValidator(contract, df).validate()
        assert passed
        assert errors == []

    def test_schema_missing_required(self):
        contract = _contract("schema_contract.yaml")
        df = _df("schema_missing_required.csv")
        passed, errors = SchemaValidator(contract, df).validate()
        assert not passed
        assert any("Required field 'email'" in err for err in errors)

    def test_schema_type_mismatch(self):
        contract = _contract("schema_contract.yaml")
        df = _df("schema_type_mismatch.csv")
        passed, errors = SchemaValidator(contract, df).validate()
        assert not passed
        assert any("type mismatch" in err for err in errors)

    def test_schema_extra_columns_warn(self):
        contract = _contract("schema_extra_columns_warn_contract.yaml")
        df = _df("schema_extra_columns_warn.csv")
        passed, errors = SchemaValidator(contract, df).validate()
        assert passed
        assert any(err.startswith("WARN") for err in errors)

    def test_schema_drift_warn(self):
        contract = _contract("schema_drift_warn_contract.yaml")
        df = _df("schema_drift_warn.csv")
        passed, errors = SchemaValidator(contract, df).validate()
        assert passed
        assert any(err.startswith("WARN") for err in errors)

    def test_schema_drift_error(self):
        contract = _contract("schema_drift_error_contract.yaml")
        df = _df("schema_drift_error.csv")
        passed, errors = SchemaValidator(contract, df).validate()
        assert not passed
        assert any(err.startswith("ERROR") for err in errors)

    def test_schema_extra_columns_error(self):
        contract = _contract("schema_extra_columns_error_contract.yaml")
        df = _df("schema_extra_columns_warn.csv")
        passed, errors = SchemaValidator(contract, df).validate()
        assert not passed
        assert any(err.startswith("ERROR") for err in errors)


class TestQualityRulesExhaustive:
    def test_quality_valid(self):
        contract = _contract("quality_contract.yaml")
        df = _df("quality_valid.csv")
        passed, errors = QualityValidator(contract, df).validate()
        assert passed
        assert errors == []

    def test_quality_nulls(self):
        contract = _contract("quality_contract.yaml")
        df = _df("quality_nulls.csv")
        passed, errors = QualityValidator(contract, df).validate()
        assert not passed
        assert any("not_null" in err for err in errors)

    def test_quality_duplicates(self):
        contract = _contract("quality_contract.yaml")
        df = _df("quality_duplicates.csv")
        passed, errors = QualityValidator(contract, df).validate()
        assert not passed
        assert any("unique" in err for err in errors)

    def test_quality_minmax_boundary(self):
        contract = _contract("quality_contract.yaml")
        df = _df("quality_minmax_boundary.csv")
        passed, errors = QualityValidator(contract, df).validate()
        assert passed
        assert errors == []

    def test_quality_minmax_fail(self):
        contract = _contract("quality_contract.yaml")
        df = _df("quality_minmax_fail.csv")
        passed, errors = QualityValidator(contract, df).validate()
        assert not passed
        assert any("min" in err or "max" in err for err in errors)

    def test_quality_enum_boundary(self):
        contract = _contract("quality_contract.yaml")
        df = _df("quality_enum_boundary.csv")
        passed, errors = QualityValidator(contract, df).validate()
        assert passed
        assert errors == []

    def test_quality_enum_fail(self):
        contract = _contract("quality_contract.yaml")
        df = _df("quality_enum_fail.csv")
        passed, errors = QualityValidator(contract, df).validate()
        assert not passed
        assert any("enum" in err for err in errors)

    def test_quality_regex_boundary(self):
        contract = _contract("quality_contract.yaml")
        df = _df("quality_regex_boundary.csv")
        passed, errors = QualityValidator(contract, df).validate()
        assert passed
        assert errors == []

    def test_quality_regex_fail(self):
        contract = _contract("quality_contract.yaml")
        df = _df("quality_regex_fail.csv")
        passed, errors = QualityValidator(contract, df).validate()
        assert not passed
        assert any("regex" in err for err in errors)

    def test_quality_max_null_ratio_boundary(self):
        contract = _contract("quality_contract.yaml")
        df = _df("quality_max_null_ratio_boundary.csv")
        passed, errors = QualityValidator(contract, df).validate()
        assert passed
        assert errors == []

    def test_quality_max_null_ratio_fail(self):
        contract = _contract("quality_contract.yaml")
        df = _df("quality_max_null_ratio_fail.csv")
        passed, errors = QualityValidator(contract, df).validate()
        assert not passed
        assert any("max_null_ratio" in err for err in errors)


class TestSeverityExhaustive:
    def test_rule_severity_valid(self):
        contract = _contract("severity_contract.yaml")
        df = _df("severity_valid.csv")
        passed, errors = QualityValidator(contract, df).validate()
        assert passed
        assert errors == []

    def test_rule_severity_warn(self):
        contract = _contract("severity_contract.yaml")
        df = _df("severity_fail.csv")
        passed, errors = QualityValidator(contract, df).validate()
        assert passed
        assert any(err.startswith("WARN") for err in errors)

    def test_rule_severity_override(self):
        contract = _contract("severity_override_contract.yaml")
        df = _df("severity_fail.csv")
        validator = QualityValidator(
            contract,
            df,
            severity_overrides={"score.max": "warn"},
        )
        passed, errors = validator.validate()
        assert passed
        assert any(err.startswith("WARN") for err in errors)

    def test_rule_severity_invalid(self):
        contract_data = {
            "contract": {"name": "invalid_severity", "version": "2.0.0"},
            "dataset": {"name": "invalid_severity"},
            "fields": [
                {
                    "name": "score",
                    "type": "integer",
                    "rules": {
                        "max": {
                            "value": 10,
                            "severity": "BAD",
                        }
                    },
                }
            ],
        }
        with pytest.raises(ValueError):
            Contract._from_dict(contract_data)

    def test_invalid_severity_override_format(self):
        with pytest.raises(ValueError):
            _parse_severity_overrides(["invalid"])


class TestDistributionExhaustive:
    def test_distribution_valid(self):
        contract = _contract("distribution_contract.yaml")
        df = _df("distribution_valid.csv")
        passed, warnings = DistributionValidator(contract, df).validate()
        assert passed
        assert warnings == []

    def test_distribution_drift(self):
        contract = _contract("distribution_contract.yaml")
        df = _df("distribution_drift.csv")
        passed, warnings = DistributionValidator(contract, df).validate()
        assert not passed
        assert any("mean drift" in warn for warn in warnings)

    def test_distribution_boundary(self):
        contract = _contract("distribution_contract.yaml")
        df = _df("distribution_boundary.csv")
        passed, warnings = DistributionValidator(contract, df).validate()
        assert passed
        assert warnings == []


class TestSLAAndFreshnessExhaustive:
    def test_sla_min_boundary(self):
        contract = _contract("sla_contract.yaml")
        df = _df("sla_min_ok.csv")
        passed, errors = SLAValidator(contract, df).validate()
        assert passed
        assert errors == []

    def test_sla_max_boundary(self):
        contract = _contract("sla_contract.yaml")
        df = _df("sla_max_ok.csv")
        passed, errors = SLAValidator(contract, df).validate()
        assert passed
        assert errors == []

    def test_sla_min_fail(self):
        contract = _contract("sla_contract.yaml")
        df = _df("sla_min_fail.csv")
        passed, errors = SLAValidator(contract, df).validate()
        assert not passed
        assert any("min_rows" in err for err in errors)

    def test_sla_max_fail_warn(self):
        contract = _contract("sla_contract.yaml")
        df = _df("sla_max_fail.csv")
        passed, errors = SLAValidator(contract, df).validate()
        assert passed
        assert any(err.startswith("WARN") for err in errors)

    def test_freshness_ok(self):
        contract_data = {
            "contract": {"name": "fresh_ok", "version": "2.0.0"},
            "dataset": {"name": "fresh_ok"},
            "fields": [
                {
                    "name": "event_time",
                    "type": "string",
                    "rules": {"freshness_max_age_hours": 24},
                }
            ],
        }
        contract = Contract._from_dict(contract_data)
        df = _df("freshness_ok.csv")
        passed, errors = QualityValidator(contract, df).validate()
        assert passed
        assert errors == []

    def test_freshness_boundary(self):
        df = _df("freshness_boundary.csv")
        parsed = pd.to_datetime(df["event_time"], errors="coerce", utc=True)
        max_ts = parsed.max()
        age_hours = (pd.Timestamp.utcnow() - max_ts).total_seconds() / 3600
        contract_data = {
            "contract": {"name": "fresh_boundary", "version": "2.0.0"},
            "dataset": {"name": "fresh_boundary"},
            "fields": [
                {
                    "name": "event_time",
                    "type": "string",
                    "rules": {"freshness_max_age_hours": age_hours + 0.01},
                }
            ],
        }
        contract = Contract._from_dict(contract_data)
        passed, errors = QualityValidator(contract, df).validate()
        assert passed
        assert errors == []

    def test_freshness_fail(self):
        contract_data = {
            "contract": {"name": "fresh_fail", "version": "2.0.0"},
            "dataset": {"name": "fresh_fail"},
            "fields": [
                {
                    "name": "event_time",
                    "type": "string",
                    "rules": {"freshness_max_age_hours": 24},
                }
            ],
        }
        contract = Contract._from_dict(contract_data)
        df = _df("freshness_fail.csv")
        passed, errors = QualityValidator(contract, df).validate()
        assert not passed
        assert any("freshness" in err.lower() for err in errors)


class TestChunkedAndSamplingExhaustive:
    def test_chunked_size_one(self):
        ds = DataSource(str(FIXTURES_DIR / "chunked_small.csv"))
        chunks = list(ds.iter_chunks(1))
        assert len(chunks) == 3
        assert all(len(chunk) == 1 for chunk in chunks)

    def test_chunked_empty(self):
        ds = DataSource(str(FIXTURES_DIR / "chunked_empty.csv"))
        chunks = list(ds.iter_chunks(2))
        assert sum(len(chunk) for chunk in chunks) == 0

    def test_sampling_rows_deterministic(self):
        ds = DataSource(str(FIXTURES_DIR / "sampling_data.csv"))
        sample_a = ds.sample_dataframe(sample_rows=4, seed=123)
        sample_b = ds.sample_dataframe(sample_rows=4, seed=123)
        assert sample_a.equals(sample_b)
        assert len(sample_a) == 4

    def test_sampling_frac_deterministic(self):
        ds = DataSource(str(FIXTURES_DIR / "sampling_data.csv"))
        sample_a = ds.sample_dataframe(sample_frac=0.3, seed=99)
        sample_b = ds.sample_dataframe(sample_frac=0.3, seed=99)
        assert sample_a.equals(sample_b)
        assert len(sample_a) == 3


class TestCustomRulesExhaustive:
    def test_custom_rule_missing(self):
        contract = _contract("custom_rules_missing_rule_contract.yaml")
        df = _df("sampling_data.csv")
        validator = CustomRuleValidator(
            contract,
            df,
            ["tests.plugins.sample_plugin"],
        )
        passed, errors = validator.validate()
        assert not passed
        assert any("not found" in err for err in errors)

    def test_custom_rule_invalid_config(self):
        contract = _contract("custom_rules_invalid_config.yaml")
        df = _df("sampling_data.csv")
        validator = CustomRuleValidator(
            contract,
            df,
            ["tests.plugins.sample_plugin"],
        )
        passed, errors = validator.validate()
        assert passed
        assert errors == []


class TestPolicyPacksExhaustive:
    def test_policy_pack_unknown(self):
        with pytest.raises(ValueError):
            Contract.from_yaml(str(FIXTURES_DIR / "policy_pack_unknown.yaml"))

    def test_policy_pack_override_conflict(self):
        contract = Contract.from_yaml(
            str(FIXTURES_DIR / "policy_pack_override_conflict.yaml")
        )
        field_map = {field.name: field for field in contract.fields}
        rules = field_map["email"].rules
        assert rules is not None
        assert rules.regex == "^[a-z]+@example\\.com$"


class TestReportSinksExhaustive:
    def test_webhook_header_invalid(self):
        with pytest.raises(ValueError):
            _parse_webhook_headers(["invalid"])
