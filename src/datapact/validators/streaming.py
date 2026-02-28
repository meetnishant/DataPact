"""
Streaming validation for Kafka and other engines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional, Tuple
from collections import deque
import json
import time

import pandas as pd

from datapact.contracts import Contract, StreamingConfig
from datapact.validators.schema_validator import SchemaValidator
from datapact.validators.quality_validator import QualityValidator
from datapact.validators.distribution_validator import DistributionValidator
from datapact.validators.sla_validator import SLAValidator
from datapact.validators.custom_rule_validator import CustomRuleValidator
from datapact.normalization import NormalizationConfig, normalize_dataframe


@dataclass
class StreamMessage:
    """Represents a streaming message with parsed payload and metadata."""

    key: Optional[bytes]
    value: Optional[bytes]
    headers: Optional[List[Tuple[str, bytes]]]
    timestamp_ms: int
    payload: Optional[Dict[str, Any]]
    error: Optional[str] = None


@dataclass
class WindowResult:
    """Validation result for a single window."""

    window_start_ms: int
    window_end_ms: int
    row_count: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class StreamingEngine:
    """Base interface for streaming engines."""

    def iter_messages(
        self, max_messages: Optional[int] = None
    ) -> Iterator[StreamMessage]:
        raise NotImplementedError

    def send_dlq(self, message: StreamMessage, violations: List[str]) -> None:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError


class KafkaStreamingEngine(StreamingEngine):
    """Kafka streaming engine using confluent-kafka."""

    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        group_id: str,
        from_beginning: bool = False,
        dlq_config: Optional[Dict[str, Any]] = None,
        poll_timeout: float = 1.0,
    ):
        try:
            from confluent_kafka import Consumer, Producer  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "confluent-kafka is required for streaming. "
                "Install with: pip install 'datapact[streaming]'"
            ) from exc

        self._consumer = Consumer(
            {
                "bootstrap.servers": bootstrap_servers,
                "group.id": group_id,
                "auto.offset.reset": "earliest" if from_beginning else "latest",
                "enable.auto.commit": True,
            }
        )
        self._consumer.subscribe([topic])
        self._producer: Optional[Any] = None
        if dlq_config and dlq_config.get("enabled"):
            self._producer = Producer({"bootstrap.servers": bootstrap_servers})
        self._dlq_topic = dlq_config.get("topic") if dlq_config else None
        self._dlq_reason_field = (
            dlq_config.get("reason_field", "_datapact_violation")
            if dlq_config
            else "_datapact_violation"
        )
        self._poll_timeout = poll_timeout

    def iter_messages(
        self, max_messages: Optional[int] = None
    ) -> Iterator[StreamMessage]:
        count = 0
        while max_messages is None or count < max_messages:
            msg = self._consumer.poll(self._poll_timeout)
            if msg is None:
                yield StreamMessage(
                    key=None,
                    value=None,
                    headers=None,
                    timestamp_ms=_now_ms(),
                    payload=None,
                )
                continue
            if msg.error():
                yield StreamMessage(
                    key=None,
                    value=None,
                    headers=None,
                    timestamp_ms=_now_ms(),
                    payload=None,
                    error=str(msg.error()),
                )
                continue

            payload: Optional[Dict[str, Any]] = None
            raw_value = msg.value()
            if raw_value is not None:
                try:
                    decoded = raw_value.decode("utf-8")
                    payload_obj = json.loads(decoded)
                    if isinstance(payload_obj, dict):
                        payload = payload_obj
                except (UnicodeDecodeError, json.JSONDecodeError):
                    payload = None

            timestamp_ms = msg.timestamp()[1] if msg.timestamp() else _now_ms()
            yield StreamMessage(
                key=msg.key(),
                value=raw_value,
                headers=msg.headers(),
                timestamp_ms=timestamp_ms or _now_ms(),
                payload=payload,
            )
            count += 1

    def send_dlq(self, message: StreamMessage, violations: List[str]) -> None:
        if not self._producer or not self._dlq_topic:
            return
        payload = _build_dlq_payload(
            message,
            violations,
            self._dlq_reason_field,
        )
        self._producer.produce(
            topic=self._dlq_topic,
            value=json.dumps(payload, ensure_ascii=True).encode("utf-8"),
            key=message.key,
            headers=message.headers,
        )
        self._producer.flush(1.0)

    def close(self) -> None:
        self._consumer.close()


class StreamingValidator:
    """Run windowed validations over streaming data."""

    def __init__(
        self,
        contract: Contract,
        engine: StreamingEngine,
        config: StreamingConfig,
        severity_overrides: Optional[Dict[str, str]] = None,
        plugin_modules: Optional[List[str]] = None,
        normalization_config: Optional[NormalizationConfig] = None,
        warn_on_empty_window: bool = True,
    ):
        self.contract = contract
        self.engine = engine
        self.config = config
        self.severity_overrides = severity_overrides or {}
        self.plugin_modules = plugin_modules or []
        self.normalization_config = normalization_config or NormalizationConfig()
        self.warn_on_empty_window = warn_on_empty_window

    def run(
        self,
        mode: str = "microbatch",
        max_messages: Optional[int] = None,
    ) -> Iterator[WindowResult]:
        window_type = self.config.window.type
        duration_ms = self.config.window.duration_seconds * 1000
        slide_ms = (
            self.config.window.slide_seconds * 1000
            if self.config.window.slide_seconds
            else None
        )

        if window_type == "sliding" and slide_ms is None:
            raise ValueError("Sliding windows require slide_seconds")

        buffer: deque[StreamMessage] = deque()
        current_window_start: Optional[int] = None
        last_emit_ms: Optional[int] = None
        last_message_ts: Optional[int] = None

        for message in self.engine.iter_messages(max_messages=max_messages):
            now_ms = _now_ms()
            if message.error:
                yield WindowResult(
                    window_start_ms=now_ms,
                    window_end_ms=now_ms,
                    row_count=0,
                    warnings=[f"WARN: Kafka message error: {message.error}"],
                )
                continue

            if message.value is None and message.payload is None:
                empty_result = self._maybe_emit_empty_window(
                    window_type,
                    duration_ms,
                    slide_ms,
                    buffer,
                    current_window_start,
                    last_emit_ms,
                )
                if empty_result is not None:
                    last_emit_ms = empty_result.window_end_ms
                    yield empty_result
                continue

            ts_ms = message.timestamp_ms or now_ms
            last_message_ts = ts_ms

            if window_type == "tumbling":
                window_start = (ts_ms // duration_ms) * duration_ms
                if current_window_start is None:
                    current_window_start = window_start
                if window_start != current_window_start:
                    yield from self._emit_tumbling_window(
                        current_window_start,
                        duration_ms,
                        list(buffer),
                    )
                    buffer.clear()
                    current_window_start = window_start
                buffer.append(message)
            elif window_type == "session":
                if current_window_start is None:
                    current_window_start = ts_ms
                if last_emit_ms is None:
                    last_emit_ms = ts_ms
                if last_message_ts is not None and buffer:
                    gap_ms = ts_ms - buffer[-1].timestamp_ms
                    if gap_ms > duration_ms:
                        yield from self._emit_session_window(
                            current_window_start,
                            list(buffer),
                        )
                        buffer.clear()
                        current_window_start = ts_ms
                buffer.append(message)
            else:
                buffer.append(message)
                if last_emit_ms is None:
                    last_emit_ms = (ts_ms // slide_ms) * slide_ms
                while ts_ms >= (last_emit_ms + slide_ms):
                    window_end = last_emit_ms + slide_ms
                    window_start = window_end - duration_ms
                    window_messages = _filter_window(buffer, window_start, window_end)
                    yield from self._emit_window(window_start, window_end, window_messages)
                    last_emit_ms = window_end
                    _trim_buffer(buffer, window_start)

            if mode == "microbatch" and max_messages is not None:
                if sum(1 for msg in buffer if msg.payload is not None) >= max_messages:
                    break

        if buffer:
            if window_type == "tumbling" and current_window_start is not None:
                yield from self._emit_tumbling_window(
                    current_window_start,
                    duration_ms,
                    list(buffer),
                )
            elif window_type == "session" and current_window_start is not None:
                yield from self._emit_session_window(
                    current_window_start,
                    list(buffer),
                )
            elif window_type == "sliding" and last_emit_ms is not None:
                window_end = last_emit_ms + (slide_ms or duration_ms)
                window_start = window_end - duration_ms
                window_messages = _filter_window(buffer, window_start, window_end)
                yield from self._emit_window(window_start, window_end, window_messages)

    def _emit_tumbling_window(
        self,
        window_start: int,
        duration_ms: int,
        messages: List[StreamMessage],
    ) -> Iterator[WindowResult]:
        window_end = window_start + duration_ms
        yield from self._emit_window(window_start, window_end, messages)

    def _emit_session_window(
        self,
        window_start: int,
        messages: List[StreamMessage],
    ) -> Iterator[WindowResult]:
        if not messages:
            return iter(())
        window_end = messages[-1].timestamp_ms
        yield from self._emit_window(window_start, window_end, messages)

    def _emit_window(
        self,
        window_start: int,
        window_end: int,
        messages: List[StreamMessage],
    ) -> Iterator[WindowResult]:
        payloads: List[Dict[str, Any]] = []
        for message in messages:
            if message.payload is not None:
                payloads.append(message.payload)

        if not payloads:
            if self.warn_on_empty_window:
                yield WindowResult(
                    window_start_ms=window_start,
                    window_end_ms=window_end,
                    row_count=0,
                    warnings=["WARN: Streaming window contained zero rows"],
                )
            return

        df = pd.DataFrame(payloads)
        df = normalize_dataframe(df, self.normalization_config)
        errors, warnings = self._validate_dataframe(df)

        if any(err.startswith("ERROR") for err in errors):
            for message in messages:
                self.engine.send_dlq(message, errors)

        yield WindowResult(
            window_start_ms=window_start,
            window_end_ms=window_end,
            row_count=len(df),
            errors=errors,
            warnings=warnings,
        )

    def _validate_dataframe(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        schema_validator = SchemaValidator(self.contract, df)
        _, schema_errors = schema_validator.validate()

        quality_validator = QualityValidator(
            self.contract,
            df,
            severity_overrides=self.severity_overrides,
        )
        _, quality_errors = quality_validator.validate()

        sla_validator = SLAValidator(self.contract, df)
        _, sla_errors = sla_validator.validate()

        dist_validator = DistributionValidator(self.contract, df)
        _, dist_warnings = dist_validator.validate()

        custom_errors: List[str] = []
        if self.plugin_modules:
            custom_validator = CustomRuleValidator(
                self.contract,
                df,
                self.plugin_modules,
            )
            _, custom_errors = custom_validator.validate()

        errors = schema_errors + quality_errors + sla_errors + custom_errors
        warnings = dist_warnings
        return errors, warnings

    def _maybe_emit_empty_window(
        self,
        window_type: str,
        duration_ms: int,
        slide_ms: Optional[int],
        buffer: deque[StreamMessage],
        window_start: Optional[int],
        last_emit_ms: Optional[int],
    ) -> Optional[WindowResult]:
        if not self.warn_on_empty_window or buffer:
            return None
        now_ms = _now_ms()

        if window_type == "tumbling":
            if window_start is None:
                return None
            if now_ms - window_start >= duration_ms:
                return WindowResult(
                    window_start_ms=window_start,
                    window_end_ms=window_start + duration_ms,
                    row_count=0,
                    warnings=["WARN: Streaming window contained zero rows"],
                )
        elif window_type == "sliding":
            if last_emit_ms is None or slide_ms is None:
                return None
            if now_ms - last_emit_ms >= slide_ms:
                window_end = last_emit_ms + slide_ms
                window_start = window_end - duration_ms
                return WindowResult(
                    window_start_ms=window_start,
                    window_end_ms=window_end,
                    row_count=0,
                    warnings=["WARN: Streaming window contained zero rows"],
                )
        return None


def _now_ms() -> int:
    return int(time.time() * 1000)


def _filter_window(
    buffer: deque[StreamMessage],
    window_start: int,
    window_end: int,
) -> List[StreamMessage]:
    return [
        msg
        for msg in buffer
        if window_start <= msg.timestamp_ms < window_end
    ]


def _trim_buffer(buffer: deque[StreamMessage], window_start: int) -> None:
    while buffer and buffer[0].timestamp_ms < window_start:
        buffer.popleft()


def _build_dlq_payload(
    message: StreamMessage,
    violations: List[str],
    reason_field: str,
) -> Dict[str, Any]:
    raw_value = message.value.decode("utf-8", errors="replace") if message.value else ""
    if message.payload is not None:
        payload = dict(message.payload)
    else:
        payload = {"raw_value": raw_value}

    payload[reason_field] = {"violations": violations}
    return payload
