"""Tests for chunked validation and sampling."""

from pathlib import Path

import pandas as pd

from datapact.datasource import DataSource
from datapact.contracts import Contract
from datapact.validators import ChunkedQualityValidator


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_iter_chunks_csv():
    ds = DataSource(str(FIXTURES_DIR / "valid_customers.csv"), format="csv")
    chunks = list(ds.iter_chunks(chunksize=2))
    assert [len(chunk) for chunk in chunks] == [2, 2, 1]


def test_iter_chunks_jsonl(tmp_path):
    df = pd.read_csv(FIXTURES_DIR / "valid_customers.csv")
    jsonl_path = tmp_path / "customers.jsonl"
    df.to_json(jsonl_path, orient="records", lines=True)

    ds = DataSource(str(jsonl_path), format="jsonl")
    chunks = list(ds.iter_chunks(chunksize=2))
    assert sum(len(chunk) for chunk in chunks) == len(df)


def test_chunked_unique_across_chunks():
    contract_data = {
        "contract": {"name": "test", "version": "2.0.0"},
        "dataset": {"name": "test"},
        "fields": [
            {
                "name": "id",
                "type": "integer",
                "required": True,
                "rules": {"unique": True},
            }
        ],
    }
    contract = Contract._from_dict(contract_data)

    chunk1 = pd.DataFrame({"id": [1, 2]})
    chunk2 = pd.DataFrame({"id": [2, 3]})

    validator = ChunkedQualityValidator(contract)
    validator.process_chunk(chunk1)
    validator.process_chunk(chunk2)
    errors = validator.finalize()

    assert any("duplicate values" in err for err in errors)
