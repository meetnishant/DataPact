"""Concurrency test: run multiple validator instances concurrently against the same DataFrame."""
from pathlib import Path
import threading

import pandas as pd
import pytest

from data_contract_validator.contracts import Contract
from data_contract_validator.validators.schema_validator import SchemaValidator
from data_contract_validator.validators.quality_validator import QualityValidator
from data_contract_validator.validators.distribution_validator import (
    DistributionValidator,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _run_validators(contract_path, data_path, results, errors, idx):
    try:
        # Load contract and data inside each thread to avoid shared state
        contract = Contract.from_yaml(str(contract_path))
        df = pd.read_csv(str(data_path))

        # Run all validators to exercise thread safety
        sv = SchemaValidator(contract, df)
        sv_ok, sv_msgs = sv.validate()

        qv = QualityValidator(contract, df)
        qv_ok, qv_msgs = qv.validate()

        dv = DistributionValidator(contract, df)
        dv_ok, dv_msgs = dv.validate()

        results[idx] = {"schema": sv_ok, "quality": qv_ok, "distribution": dv_ok}
    except Exception as e:
        errors[idx] = str(e)


def test_concurrent_validators_no_exceptions():
    """Spin up multiple validator instances concurrently against the same DataFrame."""
    contract_path = FIXTURES_DIR / "customer_contract.yaml"
    data_path = FIXTURES_DIR / "valid_customers.csv"

    # Use a moderate thread count to simulate concurrent usage
    n_threads = 20
    threads = []
    results = [None] * n_threads
    errors = [None] * n_threads

    for i in range(n_threads):
        t = threading.Thread(
            target=_run_validators, args=(contract_path, data_path, results, errors, i)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Assert no thread raised exceptions
    for idx, err in enumerate(errors):
        assert err is None, f"Thread {idx} raised an exception: {err}"

    # Assert validators returned OK statuses (schema and quality should pass)
    for idx, res in enumerate(results):
        assert res is not None, f"Thread {idx} produced no result"
        assert res["schema"] is True, f"Schema validator failed in thread {idx}"
        assert res["quality"] is True, f"Quality validator failed in thread {idx}"
