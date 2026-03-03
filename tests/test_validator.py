"""Test suite for DataPact."""

import pytest
from pathlib import Path
import pandas as pd

from datapact.contracts import Contract
from datapact.datasource import DataSource
from datapact.validators import (
    SchemaValidator,
    QualityValidator,
    DistributionValidator,
    SLAValidator,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def customer_contract():
    """Load customer contract fixture."""
    # Baseline contract used across schema, quality, and distribution tests
    return Contract.from_yaml(str(FIXTURES_DIR / "customer_contract.yaml"))


@pytest.fixture
def valid_df():
    """Load valid customer data."""
    # Fully valid dataset used to confirm success paths
    return pd.read_csv(FIXTURES_DIR / "valid_customers.csv")


@pytest.fixture
def invalid_df():
    """Load invalid customer data."""
    # Dataset with intentional violations for negative tests
    return pd.read_csv(FIXTURES_DIR / "invalid_customers.csv")


@pytest.fixture
def freshness_contract():
    return Contract.from_yaml(str(FIXTURES_DIR / "freshness_contract.yaml"))


@pytest.fixture
def freshness_df():
    return pd.read_csv(FIXTURES_DIR / "freshness_events.csv")


class TestSchemaValidator:
    """Tests for schema validation."""

    def test_valid_schema(self, customer_contract, valid_df):
        """Test valid schema passes."""
        validator = SchemaValidator(customer_contract, valid_df)
        passed, errors = validator.validate()
        # Should pass basic schema checks
        schema_errors = [e for e in errors if e.startswith("ERROR: Required")]
        assert len(schema_errors) == 0

    def test_missing_required_field(self, customer_contract):
        """Test missing required field fails."""
        df = pd.DataFrame(
            {
                "email": ["test@example.com"],
                "age": [25],
            }
        )
        validator = SchemaValidator(customer_contract, df)
        passed, errors = validator.validate()
        assert not passed
        assert any("customer_id" in e for e in errors)

    def test_extra_columns_error_severity(self):
        contract_data = {
            "contract": {"name": "test", "version": "2.0.0"},
            "dataset": {"name": "test"},
            "schema": {"extra_columns": {"severity": "ERROR"}},
            "fields": [
                {"name": "id", "type": "integer", "required": True},
            ],
        }
        contract = Contract._from_dict(contract_data)
        df = pd.DataFrame({"id": [1], "extra": ["x"]})

        validator = SchemaValidator(contract, df)
        passed, errors = validator.validate()
        assert not passed
        assert any(err.startswith("ERROR") for err in errors)


class TestQualityValidator:
    """Tests for quality validation."""

    def test_valid_data(self, customer_contract, valid_df):
        """Test valid data passes quality checks."""
        validator = QualityValidator(customer_contract, valid_df)
        passed, errors = validator.validate()
        assert passed
        assert len(errors) == 0

    def test_invalid_email_regex(self, customer_contract, invalid_df):
        """Test regex constraint failure."""
        validator = QualityValidator(customer_contract, invalid_df)
        passed, errors = validator.validate()
        assert not passed
        assert any("regex" in e.lower() for e in errors)

    def test_null_constraint(self):
        """Test not_null constraint."""
        # Build a minimal contract-like object with only the required rule
        contract = Contract(
            name="test",
            version="1.0",
            dataset=None,
            fields=[],
        )
        df = pd.DataFrame(
            {
                "required_field": [1, 2, None],
            }
        )
        # Use lightweight field/rules objects to avoid full YAML parsing
        contract.fields = [
            type(
                "Field",
                (),
                {
                    "name": "required_field",
                    "type": "integer",
                    "rules": type(
                        "Rules",
                        (),
                        {
                            "not_null": True,
                            "unique": False,
                            "min": None,
                            "max": None,
                            "regex": None,
                            "enum": None,
                            "max_null_ratio": None,
                            "freshness_max_age_hours": None,
                        },
                    )(),
                    "distribution": None,
                },
            )(),
        ]
        validator = QualityValidator(contract, df)
        passed, errors = validator.validate()
        assert not passed
        assert any("null" in e.lower() for e in errors)

    def test_enum_constraint(self):
        """Test enum constraint."""
        # Build a minimal contract-like object with an enum rule
        contract = Contract(
            name="test",
            version="1.0",
            dataset=None,
            fields=[],
        )
        df = pd.DataFrame(
            {
                "status": ["active", "inactive", "unknown"],
            }
        )
        # Use lightweight field/rules objects to avoid full YAML parsing
        contract.fields = [
            type(
                "Field",
                (),
                {
                    "name": "status",
                    "type": "string",
                    "rules": type(
                        "Rules",
                        (),
                        {
                            "not_null": False,
                            "unique": False,
                            "min": None,
                            "max": None,
                            "regex": None,
                            "enum": ["active", "inactive"],
                            "max_null_ratio": None,
                            "freshness_max_age_hours": None,
                        },
                    )(),
                    "distribution": None,
                },
            )(),
        ]
        validator = QualityValidator(contract, df)
        passed, errors = validator.validate()
        assert not passed
        assert any("enum" in e.lower() for e in errors)

    def test_rule_severity_warn(self):
        contract_data = {
            "contract": {"name": "test", "version": "2.0.0"},
            "dataset": {"name": "test"},
            "fields": [
                {
                    "name": "status",
                    "type": "string",
                    "required": True,
                    "rules": {"not_null": {"value": True, "severity": "WARN"}},
                }
            ],
        }
        contract = Contract._from_dict(contract_data)
        df = pd.DataFrame({"status": [None]})

        validator = QualityValidator(contract, df)
        passed, errors = validator.validate()
        assert passed
        assert any(err.startswith("WARN") for err in errors)

    def test_rule_severity_override(self):
        contract_data = {
            "contract": {"name": "test", "version": "2.0.0"},
            "dataset": {"name": "test"},
            "fields": [
                {
                    "name": "status",
                    "type": "string",
                    "required": True,
                    "rules": {"not_null": True},
                }
            ],
        }
        contract = Contract._from_dict(contract_data)
        df = pd.DataFrame({"status": [None]})

        validator = QualityValidator(
            contract,
            df,
            severity_overrides={"status.not_null": "warn"},
        )
        passed, errors = validator.validate()
        assert passed
        assert any(err.startswith("WARN") for err in errors)

    def test_freshness_max_age_hours(self, freshness_contract, freshness_df):
        validator = QualityValidator(freshness_contract, freshness_df)
        passed, errors = validator.validate()
        assert not passed
        assert any("freshness" in err.lower() for err in errors)


class TestDataSource:
    """Tests for data source loading."""

    def test_load_csv(self):
        """Test CSV loading."""
        ds = DataSource(str(FIXTURES_DIR / "valid_customers.csv"))
        df = ds.load()
        assert len(df) == 5
        assert "customer_id" in df.columns

    def test_detect_format(self):
        """Test format auto-detection."""
        ds = DataSource(str(FIXTURES_DIR / "valid_customers.csv"))
        assert ds.format == "csv"

    def test_infer_schema(self):
        """Test schema inference."""
        ds = DataSource(str(FIXTURES_DIR / "valid_customers.csv"))
        schema = ds.infer_schema()
        assert "customer_id" in schema
        assert schema["customer_id"] == "integer"
        assert schema["email"] == "string"

    def test_load_excel_xlsx(self):
        """Test Excel (.xlsx) file loading."""
        excel_file = FIXTURES_DIR / "valid_customers.xlsx"
        if not excel_file.exists():
            pytest.skip("valid_customers.xlsx not found")
        
        ds = DataSource(str(excel_file))
        df = ds.load()
        assert len(df) == 5
        assert "customer_id" in df.columns
        assert "email" in df.columns

    def test_detect_format_excel(self):
        """Test Excel format auto-detection."""
        excel_file = FIXTURES_DIR / "valid_customers.xlsx"
        if not excel_file.exists():
            pytest.skip("valid_customers.xlsx not found")
        
        ds = DataSource(str(excel_file))
        assert ds.format == "excel"

    def test_infer_schema_excel(self):
        """Test schema inference from Excel files."""
        excel_file = FIXTURES_DIR / "valid_customers.xlsx"
        if not excel_file.exists():
            pytest.skip("valid_customers.xlsx not found")
        
        ds = DataSource(str(excel_file))
        schema = ds.infer_schema()
        assert "customer_id" in schema
        assert schema["customer_id"] == "integer"
        assert schema["email"] == "string"

    def test_excel_sheet_selection_default(self):
        """Test Excel sheet selection (default to first sheet)."""
        excel_file = FIXTURES_DIR / "valid_customers.xlsx"
        if not excel_file.exists():
            pytest.skip("valid_customers.xlsx not found")
        
        # Default sheet_name=0 (first sheet)
        ds = DataSource(str(excel_file), sheet_name=0)
        df = ds.load()
        assert len(df) == 5  # valid_customers.xlsx has 5 rows

    def test_excel_chunking_not_supported(self):
        """Test that Excel format does not support chunking."""
        excel_file = FIXTURES_DIR / "valid_customers.xlsx"
        if not excel_file.exists():
            pytest.skip("valid_customers.xlsx not found")
        
        ds = DataSource(str(excel_file))
        with pytest.raises(ValueError, match="not supported for excel"):
            list(ds.iter_chunks(chunksize=1000))


class TestExcelValidationIntegration:
    """Integration tests for Excel file validation."""

    def test_full_validation_with_excel(self):
        """Test full validation pipeline (schema + quality) with Excel file."""
        excel_file = FIXTURES_DIR / "valid_customers.xlsx"
        if not excel_file.exists():
            pytest.skip("valid_customers.xlsx not found")
        
        # Load contract and Excel data
        contract = Contract.from_yaml(str(FIXTURES_DIR / "customer_contract.yaml"))
        ds = DataSource(str(excel_file))
        df = ds.load()
        
        # Run schema validation
        schema_validator = SchemaValidator(contract, df)
        schema_passed, schema_errors = schema_validator.validate()
        assert schema_passed, f"Schema validation failed: {schema_errors}"
        
        # Run quality validation
        severity_overrides = {}
        quality_validator = QualityValidator(contract, df, severity_overrides)
        quality_passed, quality_errors = quality_validator.validate()
        assert quality_passed, f"Quality validation failed: {quality_errors}"

    def test_invalid_excel_schema_validation(self):
        """Test validation fails on schema errors in Excel file."""
        excel_file = FIXTURES_DIR / "schema_missing_required.xlsx"
        if not excel_file.exists():
            pytest.skip("schema_missing_required.xlsx not found")
        
        contract = Contract.from_yaml(str(FIXTURES_DIR / "schema_contract.yaml"))
        ds = DataSource(str(excel_file))
        df = ds.load()
        
        # Schema validation should fail
        schema_validator = SchemaValidator(contract, df)
        schema_passed, schema_errors = schema_validator.validate()
        assert not schema_passed
        assert len(schema_errors) > 0


class TestDistributionValidator:

    """Tests for distribution validation."""

    def test_normal_distribution(self, customer_contract, valid_df):
        """Test distribution check passes."""
        validator = DistributionValidator(customer_contract, valid_df)
        passed, warnings = validator.validate()
        # Should not produce warnings for sample data
        assert len(warnings) == 0


class TestSLAValidator:
    def test_min_rows_violation(self):
        contract_data = {
            "contract": {"name": "test", "version": "2.0.0"},
            "dataset": {"name": "test"},
            "sla": {"min_rows": 2},
            "fields": [
                {"name": "id", "type": "integer", "required": True},
            ],
        }
        contract = Contract._from_dict(contract_data)
        df = pd.DataFrame({"id": [1]})

        validator = SLAValidator(contract, df)
        passed, errors = validator.validate()
        assert not passed
        assert any("min_rows" in err for err in errors)

    def test_max_rows_warn_severity(self):
        contract_data = {
            "contract": {"name": "test", "version": "2.0.0"},
            "dataset": {"name": "test"},
            "sla": {"max_rows": {"value": 1, "severity": "WARN"}},
            "fields": [
                {"name": "id", "type": "integer", "required": True},
            ],
        }
        contract = Contract._from_dict(contract_data)
        df = pd.DataFrame({"id": [1, 2]})

        validator = SLAValidator(contract, df)
        passed, errors = validator.validate()
        assert passed
        assert any(err.startswith("WARN") for err in errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
