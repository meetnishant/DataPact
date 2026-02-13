"""
Multiprocessing concurrency test: spawn multiple processes each running
validators against the same DataFrame.
"""

from pathlib import Path
from multiprocessing import get_context, Manager


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _mp_run_validators(contract_path, data_path, results, errors, idx):
    try:
        # Import inside process to avoid pickling complex modules
        from datapact.contracts import Contract
        from datapact.validators.schema_validator import (
            SchemaValidator,
        )
        from datapact.validators.quality_validator import (
            QualityValidator,
        )
        from datapact.validators.distribution_validator import (
            DistributionValidator,
        )
        import pandas as pd

        # Load contract and data inside each process to avoid shared state
        contract = Contract.from_yaml(str(contract_path))
        df = pd.read_csv(str(data_path))

        sv_ok, _ = SchemaValidator(contract, df).validate()
        qv_ok, _ = QualityValidator(contract, df).validate()
        dv_ok, _ = DistributionValidator(contract, df).validate()

        results[idx] = {"schema": sv_ok, "quality": qv_ok, "distribution": dv_ok}
    except Exception as e:
        errors[idx] = str(e)


def test_multiprocess_validators_no_exceptions():
    contract_path = FIXTURES_DIR / "customer_contract.yaml"
    data_path = FIXTURES_DIR / "valid_customers.csv"

    # Use a moderate process count to simulate multi-worker validation
    n_procs = 8
    ctx = get_context("spawn")
    manager = Manager()
    results = manager.list([None] * n_procs)
    errors = manager.list([None] * n_procs)

    procs = []
    for i in range(n_procs):
        p = ctx.Process(
            target=_mp_run_validators,
            args=(contract_path, data_path, results, errors, i),
        )
        procs.append(p)
        p.start()

    for p in procs:
        p.join()

    # Ensure no process raised exceptions
    for idx, err in enumerate(errors):
        assert err is None, f"Process {idx} raised an exception: {err}"

    # Ensure results are present and validators passed
    for idx, res in enumerate(results):
        assert res is not None, f"Process {idx} produced no result"
        assert res["schema"] is True, f"Schema validator failed in process {idx}"
        assert res["quality"] is True, f"Quality validator failed in process {idx}"
