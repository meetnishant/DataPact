"""Test suite for data contract validator."""

import pytest
from pathlib import Path
import pandas as pd

from data_contract_validator.contracts import Contract
from data_contract_validator.datasource import DataSource
from data_contract_validator.validators import (
    SchemaValidator,
    QualityValidator,
    DistributionValidator,
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
        df = pd.DataFrame({
            "email": ["test@example.com"],
            "age": [25],
        })
        validator = SchemaValidator(customer_contract, df)
        passed, errors = validator.validate()
        assert not passed
        assert any("customer_id" in e for e in errors)


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
        df = pd.DataFrame({
            "required_field": [1, 2, None],
        })
        # Use lightweight field/rules objects to avoid full YAML parsing
        contract.fields = [
            type('Field', (), {
                'name': 'required_field',
                'type': 'integer',
                'rules': type('Rules', (), {
                    'not_null': True,
                    'unique': False,
                    'min': None,
                    'max': None,
                    'regex': None,
                    'enum': None,
                    'max_null_ratio': None,
                })(),
                'distribution': None,
            })(),
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
        df = pd.DataFrame({
            "status": ["active", "inactive", "unknown"],
        })
        # Use lightweight field/rules objects to avoid full YAML parsing
        contract.fields = [
            type('Field', (), {
                'name': 'status',
                'type': 'string',
                'rules': type('Rules', (), {
                    'not_null': False,
                    'unique': False,
                    'min': None,
                    'max': None,
                    'regex': None,
                    'enum': ["active", "inactive"],
                    'max_null_ratio': None,
                })(),
                'distribution': None,
            })(),
        ]
        validator = QualityValidator(contract, df)
        passed, errors = validator.validate()
        assert not passed
        assert any("enum" in e.lower() for e in errors)


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


class TestDistributionValidator:
    """Tests for distribution validation."""

    def test_normal_distribution(self, customer_contract, valid_df):
        """Test distribution check passes."""
        validator = DistributionValidator(customer_contract, valid_df)
        passed, warnings = validator.validate()
        # Should not produce warnings for sample data
        assert len(warnings) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
