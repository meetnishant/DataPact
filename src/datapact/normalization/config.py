"""Configuration for normalization behavior."""

from dataclasses import dataclass


@dataclass
class NormalizationConfig:
    """Normalization settings (noop by default)."""

    mode: str = "none"
    flatten_separator: str = "."
