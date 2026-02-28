import json
import time
from typing import List

import pytest

from datapact.contracts import Contract
from datapact.validators.streaming import StreamingValidator, KafkaStreamingEngine


pytest.importorskip("confluent_kafka")
pytest.importorskip("testcontainers")

from confluent_kafka import Producer, Consumer  # noqa: E402
from testcontainers.kafka import KafkaContainer  # noqa: E402


def _build_contract(topic: str) -> Contract:
    contract_data = {
        "contract": {"name": "stream_contract", "version": "2.0.0"},
        "dataset": {"name": "events"},
        "fields": [
            {"name": "id", "type": "integer", "required": True, "rules": {}},
            {"name": "value", "type": "float", "required": False, "rules": {}},
        ],
        "streaming": {
            "engine": "kafka",
            "topic": topic,
            "consumer_group": "datapact-validator",
            "window": {"type": "tumbling", "duration_seconds": 5},
            "metrics": ["row_rate", "mean", "std"],
            "dlq": {
                "enabled": True,
                "topic": f"{topic}.dlq",
                "reason_field": "_datapact_violation",
            },
        },
    }
    return Contract._from_dict(contract_data)


def _produce_messages(bootstrap: str, topic: str, payloads: List[dict]) -> None:
    producer = Producer({"bootstrap.servers": bootstrap})
    for payload in payloads:
        producer.produce(topic, json.dumps(payload).encode("utf-8"))
    producer.flush(5.0)


def _consume_one(bootstrap: str, topic: str, group_id: str) -> dict:
    consumer = Consumer(
        {
            "bootstrap.servers": bootstrap,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
        }
    )
    consumer.subscribe([topic])
    start = time.time()
    while time.time() - start < 10:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            continue
        data = json.loads(msg.value().decode("utf-8"))
        consumer.close()
        return data
    consumer.close()
    raise AssertionError("No DLQ message received")


def test_streaming_kafka_window_validation() -> None:
    with KafkaContainer() as kafka:
        bootstrap = kafka.get_bootstrap_server()
        topic = "datapact-events"
        contract = _build_contract(topic)

        payloads = [
            {"id": 1, "value": 10.0},
            {"id": 2, "value": 12.5},
            {"id": 3, "value": 9.0},
        ]
        _produce_messages(bootstrap, topic, payloads)

        engine = KafkaStreamingEngine(
            bootstrap_servers=bootstrap,
            topic=topic,
            group_id="datapact-test",
            from_beginning=True,
            dlq_config={"enabled": False},
        )
        validator = StreamingValidator(
            contract=contract,
            engine=engine,
            config=contract.streaming,
            warn_on_empty_window=False,
        )

        results = []
        for result in validator.run(max_messages=3, mode="microbatch"):
            if result.row_count > 0:
                results.append(result)
                break
        engine.close()

        assert results
        assert all(
            not any(err.startswith("ERROR") for err in res.errors)
            for res in results
        )


def test_streaming_kafka_dlq_on_error() -> None:
    with KafkaContainer() as kafka:
        bootstrap = kafka.get_bootstrap_server()
        topic = "datapact-errors"
        contract = _build_contract(topic)

        payloads = [{"value": 10.0}]
        _produce_messages(bootstrap, topic, payloads)

        engine = KafkaStreamingEngine(
            bootstrap_servers=bootstrap,
            topic=topic,
            group_id="datapact-test-dlq",
            from_beginning=True,
            dlq_config={
                "enabled": True,
                "topic": f"{topic}.dlq",
                "reason_field": "_datapact_violation",
            },
        )
        validator = StreamingValidator(
            contract=contract,
            engine=engine,
            config=contract.streaming,
            warn_on_empty_window=False,
        )

        for _ in validator.run(max_messages=1, mode="microbatch"):
            break
        engine.close()

        dlq_payload = _consume_one(bootstrap, f"{topic}.dlq", "dlq-consumer")
        assert "_datapact_violation" in dlq_payload
