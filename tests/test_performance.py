import os
import time
import psutil
import pytest
import pandas as pd


# Helper to run CLI as subprocess for timing
import subprocess


def run_cli_validate(contract_path, data_path):
    start = time.time()
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    result = subprocess.run([
        "python3", "-m", "src.datapact.cli", "validate",
        "--contract", contract_path,
        "--data", data_path
    ], capture_output=True, env=env)
    elapsed = time.time() - start
    return result, elapsed

@pytest.mark.performance
def test_large_csv_validation_time():
    # Use pre-generated large contract and matching data
    contract_path = "tests/fixtures/large_contract.yaml"
    data_path = "tests/fixtures/large_contract_data.csv"
    result, elapsed = run_cli_validate(contract_path, data_path)
    assert result.returncode == 0
    assert elapsed < 60  # Example SLA: 10k rows validated in under 60s

@pytest.mark.performance
def test_contract_parsing_speed():
    # Parse a contract with 100 fields, 50 rules each
    contract_path = "tests/fixtures/large_contract.yaml"
    start = time.time()
    import sys
    sys.path.insert(0, "src")
    from src.datapact.contracts import Contract
    Contract.from_yaml(contract_path)
    elapsed = time.time() - start
    assert elapsed < 2  # Example: parse in under 2s

@pytest.mark.performance
def test_cli_startup_time():
    contract_path = "tests/fixtures/large_contract.yaml"
    data_path = "tests/fixtures/large_contract_data.csv"
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
    assert elapsed < 2  # Startup + small validation <2s

@pytest.mark.performance
def test_memory_usage_large_file(tmp_path):
    # Generate 500MB CSV
    rows, cols = 2_000_000, 10
    df = pd.DataFrame({f"col{i}": range(rows) for i in range(cols)})
    csv_path = tmp_path / "large_mem.csv"
    df.to_csv(csv_path, index=False)
    contract_path = "tests/fixtures/schema_contract.yaml"
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss
    from src.datapact.datasource import DataSource
    ds = DataSource(str(csv_path))
    df_loaded = ds.load()
    mem_after = process.memory_info().rss
    # Allow up to 4x file size in RAM (looser threshold for pandas)
    file_size = os.path.getsize(csv_path)
    assert (mem_after - mem_before) < 4 * file_size

@pytest.mark.performance
def test_batch_validation_time(tmp_path):
    # Validate 100 small files in batch
    contract_path = "tests/fixtures/large_contract.yaml"
    data_path = "tests/fixtures/large_contract_data.csv"
    files = [data_path] * 100
    total_start = time.time()
    for f in files:
        result, elapsed = run_cli_validate(contract_path, str(f))
        assert result.returncode == 0
        assert elapsed < 2  # Each file <2s
    total_elapsed = time.time() - total_start
    assert total_elapsed < 180  # All 100 in under 3min
