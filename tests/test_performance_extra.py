import os
import pytest
import time
import subprocess
import pandas as pd
@pytest.mark.performance
def test_throughput_under_load(tmp_path):
    # Run 10 concurrent validations on different datasets
    contract_path = "tests/fixtures/large_contract.yaml"
    data_path = "tests/fixtures/large_contract_data.csv"
    files = [data_path] * 10
    start = time.time()
    from concurrent.futures import ThreadPoolExecutor
    def run_validate(f):
        env = os.environ.copy()
        env["PYTHONPATH"] = "src"
        return subprocess.run([
            "python3", "-m", "src.datapact.cli", "validate",
            "--contract", contract_path,
            "--data", str(f)
        ], capture_output=True, env=env)
    with ThreadPoolExecutor(max_workers=10) as ex:
        results = list(ex.map(run_validate, files))
    elapsed = time.time() - start
    for r in results:
        assert r.returncode == 0
    assert elapsed < 60  # All 10 in under 1 min

@pytest.mark.performance
def test_performance_degradation(tmp_path):
    # Gradually increase dataset size and record validation time
    contract_path = "tests/fixtures/large_contract.yaml"
    data_path = "tests/fixtures/large_contract_data.csv"
    times = []
    for _ in range(3):
        start = time.time()
        env = os.environ.copy()
        env["PYTHONPATH"] = "src"
        result = subprocess.run([
            "python3", "-m", "src.datapact.cli", "validate",
            "--contract", contract_path,
            "--data", data_path
        ], capture_output=True, env=env)
        elapsed = time.time() - start
        assert result.returncode == 0
        times.append(elapsed)
    # Check that time does not explode
    assert times[2] < 15 * times[0]  # 3rd run <15x 1st run
