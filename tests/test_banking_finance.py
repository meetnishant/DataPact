"""
Test cases for multi-table banking/finance data products and consumer-specific
contracts. Covers deposits and lending with strict vs aggregate consumers and
multi-table joins.
"""

from pathlib import Path

import pandas as pd
import pytest
import yaml

from datapact.contracts import Contract
from datapact.validators import SchemaValidator, QualityValidator

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load_contract_dict(filename: str) -> dict:
    with open(FIXTURES_DIR / filename, "r") as handle:
        return yaml.safe_load(handle)


@pytest.fixture
def deposits_contract():
    # Strict consumer contract for deposits accounts
    return Contract.from_yaml(str(FIXTURES_DIR / "deposits_contract.yaml"))


@pytest.fixture
def deposits_agg_contract():
    # Aggregate consumer contract with relaxed customer_id constraints
    return Contract.from_yaml(str(FIXTURES_DIR / "deposits_accounts_agg_contract.yaml"))


@pytest.fixture
def deposits_txn_contract():
    # Transactions contract for deposits product
    return Contract.from_yaml(str(FIXTURES_DIR / "deposits_transactions_contract.yaml"))


@pytest.fixture
def lending_contract():
    # Strict consumer contract for loans
    return Contract.from_yaml(str(FIXTURES_DIR / "lending_contract.yaml"))


@pytest.fixture
def lending_agg_contract():
    # Aggregate consumer contract with relaxed customer_id constraints
    return Contract.from_yaml(str(FIXTURES_DIR / "lending_loans_agg_contract.yaml"))


@pytest.fixture
def lending_payments_contract():
    # Payments contract for lending product
    return Contract.from_yaml(str(FIXTURES_DIR / "lending_payments_contract.yaml"))


@pytest.fixture
def deposits_df():
    # Deposits accounts table
    return pd.read_csv(FIXTURES_DIR / "deposits_data.csv", dtype={"open_date": str})


@pytest.fixture
def deposits_agg_df():
    # Aggregate consumer view for deposits accounts
    return pd.read_csv(
        FIXTURES_DIR / "deposits_accounts_agg.csv",
        dtype={"open_date": str},
    )


@pytest.fixture
def deposits_txn_df():
    # Deposits transactions table
    return pd.read_csv(
        FIXTURES_DIR / "deposits_transactions.csv",
        dtype={"txn_date": str},
    )


@pytest.fixture
def lending_df():
    # Lending loans table
    return pd.read_csv(
        FIXTURES_DIR / "lending_data.csv",
        dtype={"origination_date": str},
    )


@pytest.fixture
def lending_agg_df():
    # Aggregate consumer view for loans
    return pd.read_csv(
        FIXTURES_DIR / "lending_loans_agg.csv",
        dtype={"origination_date": str},
    )


@pytest.fixture
def lending_payments_df():
    # Lending payments table
    return pd.read_csv(
        FIXTURES_DIR / "lending_payments.csv",
        dtype={"payment_date": str},
    )


class TestDepositsAccountsStrict:
    @pytest.mark.PositiveCases
    def test_positive_cases(self, deposits_contract, deposits_df):
        # Positive slice: valid accounts that should pass strict rules
        df = deposits_df.iloc[0:5]
        passed, errors = SchemaValidator(deposits_contract, df).validate()
        assert passed, f"Schema errors: {errors}"
        q_passed, q_errors = QualityValidator(deposits_contract, df).validate()
        assert q_passed, f"Quality errors: {q_errors}"

    @pytest.mark.NegativeCases
    def test_negative_cases(self, deposits_contract, deposits_df):
        # Negative slice: expected to violate strict rules
        df = deposits_df.iloc[5:10]
        passed, errors = SchemaValidator(deposits_contract, df).validate()
        q_passed, q_errors = QualityValidator(deposits_contract, df).validate()
        assert not (passed and q_passed), f"Expected failure, got: {errors + q_errors}"

    @pytest.mark.BoundaryCases
    def test_boundary_cases(self, deposits_contract, deposits_df):
        # Boundary slice: edge values that should still pass
        df = deposits_df.iloc[10:15]
        passed, errors = SchemaValidator(deposits_contract, df).validate()
        q_passed, q_errors = QualityValidator(deposits_contract, df).validate()
        assert passed, f"Boundary schema errors: {errors}"
        assert q_passed, f"Boundary quality errors: {q_errors}"


class TestDepositsAccountsAggregate:
    def test_aggregate_consumer_contract(self, deposits_agg_contract, deposits_agg_df):
        # Aggregate consumer allows limited null/duplicate customer_ids
        passed, errors = SchemaValidator(
            deposits_agg_contract, deposits_agg_df
        ).validate()
        assert passed, f"Schema errors: {errors}"
        q_passed, q_errors = QualityValidator(
            deposits_agg_contract, deposits_agg_df
        ).validate()
        assert q_passed, f"Quality errors: {q_errors}"

        customer = deposits_agg_df["customer_id"]
        # Enforce tolerance targets outside the contract rules
        null_ratio = customer.isna().sum() / len(customer)
        non_null = customer.dropna()
        unique_ratio = non_null.nunique() / len(non_null)
        assert null_ratio <= 0.01, f"Null ratio too high: {null_ratio:.2%}"
        assert unique_ratio >= 0.99, f"Uniqueness ratio too low: {unique_ratio:.2%}"

    def test_max_null_ratio_empty_dataset(self, deposits_agg_contract, deposits_agg_df):
        empty_df = deposits_agg_df.iloc[0:0]
        q_passed, q_errors = QualityValidator(
            deposits_agg_contract, empty_df
        ).validate()
        assert not q_passed
        assert any(
            "cannot evaluate max_null_ratio" in err for err in q_errors
        ), f"Expected max_null_ratio error, got: {q_errors}"


class TestDepositsTransactions:
    @pytest.mark.PositiveCases
    def test_positive_cases(self, deposits_txn_contract, deposits_txn_df):
        # Positive transactions should pass contract rules
        df = deposits_txn_df.iloc[0:5]
        passed, errors = SchemaValidator(deposits_txn_contract, df).validate()
        assert passed, f"Schema errors: {errors}"
        q_passed, q_errors = QualityValidator(deposits_txn_contract, df).validate()
        assert q_passed, f"Quality errors: {q_errors}"

    @pytest.mark.NegativeCases
    def test_negative_cases(self, deposits_txn_contract, deposits_txn_df):
        # Negative transactions should fail at least one rule
        df = deposits_txn_df.iloc[5:10]
        passed, errors = SchemaValidator(deposits_txn_contract, df).validate()
        q_passed, q_errors = QualityValidator(deposits_txn_contract, df).validate()
        assert not (passed and q_passed), f"Expected failure, got: {errors + q_errors}"

    @pytest.mark.BoundaryCases
    def test_boundary_cases(self, deposits_txn_contract, deposits_txn_df):
        # Boundary transactions should pass on the edge
        df = deposits_txn_df.iloc[10:15]
        passed, errors = SchemaValidator(deposits_txn_contract, df).validate()
        q_passed, q_errors = QualityValidator(deposits_txn_contract, df).validate()
        assert passed, f"Boundary schema errors: {errors}"
        assert q_passed, f"Boundary quality errors: {q_errors}"


class TestLendingLoansStrict:
    @pytest.mark.PositiveCases
    def test_positive_cases(self, lending_contract, lending_df):
        # Positive slice: valid loans that should pass strict rules
        df = lending_df.iloc[0:5]
        passed, errors = SchemaValidator(lending_contract, df).validate()
        assert passed, f"Schema errors: {errors}"
        q_passed, q_errors = QualityValidator(lending_contract, df).validate()
        assert q_passed, f"Quality errors: {q_errors}"

    @pytest.mark.NegativeCases
    def test_negative_cases(self, lending_contract, lending_df):
        # Negative slice: expected to violate strict rules
        df = lending_df.iloc[5:10]
        passed, errors = SchemaValidator(lending_contract, df).validate()
        q_passed, q_errors = QualityValidator(lending_contract, df).validate()
        assert not (passed and q_passed), f"Expected failure, got: {errors + q_errors}"

    @pytest.mark.BoundaryCases
    def test_boundary_cases(self, lending_contract, lending_df):
        # Boundary slice: edge values that should still pass
        df = lending_df.iloc[10:15]
        passed, errors = SchemaValidator(lending_contract, df).validate()
        q_passed, q_errors = QualityValidator(lending_contract, df).validate()
        assert passed, f"Boundary schema errors: {errors}"
        assert q_passed, f"Boundary quality errors: {q_errors}"


class TestLendingLoansAggregate:
    def test_aggregate_consumer_contract(self, lending_agg_contract, lending_agg_df):
        # Aggregate consumer allows limited null/duplicate customer_ids
        passed, errors = SchemaValidator(
            lending_agg_contract, lending_agg_df
        ).validate()
        assert passed, f"Schema errors: {errors}"
        q_passed, q_errors = QualityValidator(
            lending_agg_contract, lending_agg_df
        ).validate()
        assert q_passed, f"Quality errors: {q_errors}"

        customer = lending_agg_df["customer_id"]
        # Enforce tolerance targets outside the contract rules
        null_ratio = customer.isna().sum() / len(customer)
        non_null = customer.dropna()
        unique_ratio = non_null.nunique() / len(non_null)
        assert null_ratio <= 0.01, f"Null ratio too high: {null_ratio:.2%}"
        assert unique_ratio >= 0.99, f"Uniqueness ratio too low: {unique_ratio:.2%}"


class TestLendingPayments:
    @pytest.mark.PositiveCases
    def test_positive_cases(self, lending_payments_contract, lending_payments_df):
        # Positive payments should pass contract rules
        df = lending_payments_df.iloc[0:5]
        passed, errors = SchemaValidator(lending_payments_contract, df).validate()
        assert passed, f"Schema errors: {errors}"
        q_passed, q_errors = QualityValidator(lending_payments_contract, df).validate()
        assert q_passed, f"Quality errors: {q_errors}"

    @pytest.mark.NegativeCases
    def test_negative_cases(self, lending_payments_contract, lending_payments_df):
        # Negative payments should fail at least one rule
        df = lending_payments_df.iloc[5:10]
        passed, errors = SchemaValidator(lending_payments_contract, df).validate()
        q_passed, q_errors = QualityValidator(lending_payments_contract, df).validate()
        assert not (passed and q_passed), f"Expected failure, got: {errors + q_errors}"

    @pytest.mark.BoundaryCases
    def test_boundary_cases(self, lending_payments_contract, lending_payments_df):
        # Boundary payments should pass on the edge
        df = lending_payments_df.iloc[10:15]
        passed, errors = SchemaValidator(lending_payments_contract, df).validate()
        q_passed, q_errors = QualityValidator(lending_payments_contract, df).validate()
        assert passed, f"Boundary schema errors: {errors}"
        assert q_passed, f"Boundary quality errors: {q_errors}"


class TestComplexConsumption:
    def test_deposits_position_join(self, deposits_df, deposits_txn_df):
        # Join transactions to accounts to simulate a position view
        accounts = deposits_df[deposits_df["account_id"].notna()]
        valid_txns = pd.concat(
            [deposits_txn_df.iloc[0:5], deposits_txn_df.iloc[10:15]],
            ignore_index=True,
        )
        merged = valid_txns.merge(
            accounts, on=["account_id", "customer_id"], how="left"
        )
        assert merged["balance"].notna().all(), "Unmatched transactions found"

    def test_time_window_aggregation(self, deposits_txn_df):
        # Use valid slices only to avoid NaT in rolling windows
        valid_txns = pd.concat(
            [deposits_txn_df.iloc[0:5], deposits_txn_df.iloc[10:15]],
            ignore_index=True,
        )
        valid_txns["txn_date"] = pd.to_datetime(valid_txns["txn_date"], errors="coerce")
        valid_txns = valid_txns.dropna(subset=["txn_date"]).sort_values(
            ["customer_id", "txn_date"]
        )

        rolling = (
            valid_txns.set_index("txn_date")
            .groupby("customer_id")["amount"]
            .rolling("30D", min_periods=1)
            .sum()
            .reset_index(level=0, drop=True)
        )
        valid_txns["rolling_30d_sum"] = rolling.values
        assert valid_txns["rolling_30d_sum"].isna().sum() < len(valid_txns)


class TestValidationExceptions:
    def test_invalid_regex_rule(self, tmp_path, lending_df):
        contract_data = _load_contract_dict("lending_contract.yaml")
        for field in contract_data.get("fields", []):
            if field.get("name") == "origination_date":
                field["rules"]["regex"] = "["
                break

        contract_path = tmp_path / "lending_contract_bad_regex.yaml"
        contract_path.write_text(yaml.safe_dump(contract_data))

        contract = Contract.from_yaml(str(contract_path))
        q_passed, q_errors = QualityValidator(contract, lending_df.iloc[0:5]).validate()
        assert not q_passed
        assert any(
            "invalid regex" in err for err in q_errors
        ), f"Expected invalid regex error, got: {q_errors}"

    def test_unhashable_enum_rule(self, tmp_path, deposits_df):
        contract_data = _load_contract_dict("deposits_contract.yaml")
        for field in contract_data.get("fields", []):
            if field.get("name") == "product_type":
                field["rules"]["enum"] = ["checking", ["bad"]]
                break

        contract_path = tmp_path / "deposits_contract_bad_enum.yaml"
        contract_path.write_text(yaml.safe_dump(contract_data))

        contract = Contract.from_yaml(str(contract_path))
        q_passed, q_errors = QualityValidator(
            contract, deposits_df.iloc[0:5]
        ).validate()
        assert not q_passed
        assert any(
            "enum contains unhashable values" in err for err in q_errors
        ), f"Expected enum error, got: {q_errors}"
