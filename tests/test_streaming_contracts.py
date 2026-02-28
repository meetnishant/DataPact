import pytest

from datapact.contracts import Contract


def test_streaming_contract_parses() -> None:
    contract_data = {
        "contract": {"name": "stream_contract", "version": "2.0.0"},
        "dataset": {"name": "events"},
        "fields": [
            {"name": "id", "type": "integer", "required": True, "rules": {}},
            {"name": "value", "type": "float", "required": False, "rules": {}},
        ],
        "streaming": {
            "engine": "kafka",
            "topic": "events.v1",
            "consumer_group": "datapact-validator",
            "window": {"type": "tumbling", "duration_seconds": 60},
            "metrics": ["row_rate", "mean"],
            "dlq": {
                "enabled": True,
                "topic": "events.v1.dlq",
                "reason_field": "_datapact_violation",
            },
        },
    }

    contract = Contract._from_dict(contract_data)
    assert contract.streaming is not None
    assert contract.streaming.engine == "kafka"
    assert contract.streaming.topic == "events.v1"
    assert contract.streaming.window.type == "tumbling"
    assert contract.streaming.window.duration_seconds == 60
    assert contract.streaming.dlq.enabled is True


def test_streaming_contract_requires_topic() -> None:
    contract_data = {
        "contract": {"name": "stream_contract", "version": "2.0.0"},
        "dataset": {"name": "events"},
        "fields": [
            {"name": "id", "type": "integer", "required": True, "rules": {}},
        ],
        "streaming": {
            "engine": "kafka",
            "consumer_group": "datapact-validator",
        },
    }

    with pytest.raises(ValueError, match="streaming.topic is required"):
        Contract._from_dict(contract_data)
