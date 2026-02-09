"""
Custom rule validation using plugin modules.
"""

from typing import Any, Callable, Dict, List, Tuple
import importlib
import pandas as pd

from datapact.contracts import Contract, Field


PluginRule = Callable[..., Any]


class CustomRuleValidator:
    """
    Validate custom rules loaded from plugin modules.
    """

    def __init__(self, contract: Contract, df: pd.DataFrame, plugin_modules: List[str]):
        self.contract = contract
        self.df = df
        self.plugin_modules = plugin_modules
        self.errors: List[str] = []
        self.rules = self._load_rules(plugin_modules)

    def validate(self) -> Tuple[bool, List[str]]:
        self.errors = []

        # Field-level custom rules
        for field in self.contract.fields:
            if not field.rules or not field.rules.custom:
                continue
            if field.name not in self.df.columns:
                continue
            for rule_name, config in field.rules.custom.items():
                self._run_field_rule(field, rule_name, config)

        # Dataset-level custom rules
        for rule in self.contract.custom_rules:
            rule_name = rule.get("name")
            config = rule.get("config", {})
            severity = _normalize_severity(rule.get("severity"))
            if rule_name is None:
                continue
            self._run_dataset_rule(rule_name, config, severity)

        has_errors = any(err.startswith("ERROR") for err in self.errors)
        return not has_errors, self.errors

    def _run_field_rule(self, field: Field, rule_name: str, config: Any) -> None:
        severity = _normalize_severity(
            config.get("severity") if isinstance(config, dict) else None
        )
        rule = self.rules.get(rule_name)
        if rule is None:
            self.errors.append(
                f"ERROR: Custom rule '{rule_name}' not found for field '{field.name}'"
            )
            return

        result = rule(self.df[field.name], config, field, self.df)
        self._record_result(field.name, rule_name, result, severity)

    def _run_dataset_rule(self, rule_name: str, config: Any, severity: str) -> None:
        rule = self.rules.get(rule_name)
        if rule is None:
            self.errors.append(
                f"ERROR: Custom rule '{rule_name}' not found for dataset"
            )
            return

        result = rule(self.df, config)
        self._record_result("", rule_name, result, severity)

    def _record_result(
        self,
        field_name: str,
        rule_name: str,
        result: Any,
        severity: str,
    ) -> None:
        if isinstance(result, tuple) and len(result) == 2:
            passed, message = result
            if not passed:
                self.errors.append(f"{severity}: {message}")
            return

        if isinstance(result, list):
            for message in result:
                self.errors.append(f"{severity}: {message}")
            return

        if isinstance(result, str):
            self.errors.append(f"{severity}: {result}")
            return

        if result is False:
            self.errors.append(
                f"{severity}: Custom rule '{rule_name}' failed"
            )

    @staticmethod
    def _load_rules(plugin_modules: List[str]) -> Dict[str, PluginRule]:
        rules: Dict[str, PluginRule] = {}
        for module_path in plugin_modules:
            module = importlib.import_module(module_path)
            module_rules = getattr(module, "RULES", {})
            if not isinstance(module_rules, dict):
                raise ValueError(
                    f"Plugin module {module_path} must export RULES dict"
                )
            rules.update(module_rules)
        return rules


def _normalize_severity(value: Any) -> str:
    if value is None:
        return "ERROR"
    normalized = str(value).upper()
    if normalized not in {"ERROR", "WARN"}:
        return "ERROR"
    return normalized
