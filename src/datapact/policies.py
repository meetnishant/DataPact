"""
Policy packs for reusable rule bundles.
"""

from typing import Any, Dict, List, Tuple
import copy


POLICY_PACKS: Dict[str, Dict[str, Any]] = {
    "pii_basic": {
        "fields": {
            "email": {
                "rules": {
                    "not_null": True,
                    "regex": "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$",
                }
            },
            "phone": {
                "rules": {
                    "regex": "^\\+?[0-9][0-9\\- ]{7,}$",
                }
            },
        }
    },
    "finance_basic": {
        "fields": {
            "account_id": {
                "rules": {
                    "not_null": True,
                    "unique": True,
                }
            },
            "amount": {
                "rules": {
                    "min": 0,
                }
            },
        }
    },
}


def get_policy_pack(name: str) -> Dict[str, Any]:
    if name not in POLICY_PACKS:
        raise ValueError(
            f"Unknown policy pack '{name}'. Supported packs: "
            f"{', '.join(sorted(POLICY_PACKS.keys()))}"
        )
    return copy.deepcopy(POLICY_PACKS[name])


def apply_policy_packs(data: Dict[str, Any]) -> Dict[str, Any]:
    policies = data.get("policies", [])
    if not policies:
        return data
    if not isinstance(policies, list):
        raise ValueError("policies must be a list")

    result = copy.deepcopy(data)
    fields = result.get("fields", [])
    if not isinstance(fields, list):
        raise ValueError("Contract 'fields' must be a list")

    field_map = {
        field.get("name"): field
        for field in fields
        if isinstance(field, dict) and "name" in field
    }

    schema = result.get("schema", {}) or {}
    if not isinstance(schema, dict):
        raise ValueError("schema must be a mapping")
    sla = result.get("sla", {}) or {}
    if not isinstance(sla, dict):
        raise ValueError("sla must be a mapping")
    custom_rules = result.get("custom_rules", []) or []
    if not isinstance(custom_rules, list):
        raise ValueError("custom_rules must be a list")

    original_schema_keys = set(schema.keys())
    original_sla_keys = set(sla.keys())

    for entry in policies:
        name, overrides = _normalize_policy_entry(entry)
        pack = get_policy_pack(name)
        _apply_field_policies(
            field_map,
            pack.get("fields", {}),
            overrides.get("fields", {}),
        )
        schema = _merge_top_level(
            schema,
            pack.get("schema"),
            overrides.get("schema"),
            original_schema_keys,
        )
        sla = _merge_top_level(
            sla,
            pack.get("sla"),
            overrides.get("sla"),
            original_sla_keys,
        )
        custom_rules = _merge_custom_rules(
            custom_rules,
            pack.get("custom_rules"),
            overrides.get("custom_rules"),
        )

    result["schema"] = schema
    result["sla"] = sla
    result["custom_rules"] = custom_rules
    return result


def _normalize_policy_entry(entry: Any) -> Tuple[str, Dict[str, Any]]:
    if isinstance(entry, str):
        return entry, {}
    if isinstance(entry, dict):
        name = entry.get("name")
        if not name:
            raise ValueError("Policy entry must include 'name'")
        overrides = entry.get("overrides", {}) or {}
        if not isinstance(overrides, dict):
            raise ValueError("Policy overrides must be a mapping")
        return name, overrides
    raise ValueError("Policy entry must be a string or mapping")


def _apply_field_policies(
    field_map: Dict[str, Dict[str, Any]],
    policy_fields: Any,
    override_fields: Any,
) -> None:
    if policy_fields and not isinstance(policy_fields, dict):
        raise ValueError("Policy fields must be a mapping")
    if override_fields and not isinstance(override_fields, dict):
        raise ValueError("Policy overrides fields must be a mapping")

    field_names = set((policy_fields or {}).keys()) | set((override_fields or {}).keys())
    for field_name in field_names:
        if field_name not in field_map:
            continue
        field = field_map[field_name]
        rules = field.get("rules") or {}
        if not isinstance(rules, dict):
            raise ValueError("Field rules must be a mapping")
        original_keys = set(rules.keys())

        policy_rules = (policy_fields or {}).get(field_name, {}).get("rules", {})
        override_rules = (override_fields or {}).get(field_name, {}).get("rules", {})
        if policy_rules and not isinstance(policy_rules, dict):
            raise ValueError("Policy rules must be a mapping")
        if override_rules and not isinstance(override_rules, dict):
            raise ValueError("Policy override rules must be a mapping")

        _merge_rules(rules, policy_rules, original_keys)
        _merge_rules(rules, override_rules, original_keys, force=True)
        field["rules"] = rules


def _merge_rules(
    target: Dict[str, Any],
    source: Dict[str, Any],
    original_keys: set,
    force: bool = False,
) -> None:
    for key, value in source.items():
        if key in original_keys:
            continue
        if not force and key in target:
            continue
        target[key] = value


def _merge_top_level(
    target: Dict[str, Any],
    policy: Any,
    overrides: Any,
    original_keys: set,
) -> Dict[str, Any]:
    if policy and not isinstance(policy, dict):
        raise ValueError("Policy section must be a mapping")
    if overrides and not isinstance(overrides, dict):
        raise ValueError("Policy overrides section must be a mapping")

    for key, value in (policy or {}).items():
        if key not in target:
            target[key] = value

    for key, value in (overrides or {}).items():
        if key in original_keys:
            continue
        target[key] = value

    return target


def _merge_custom_rules(
    current: List[Dict[str, Any]],
    policy_rules: Any,
    override_rules: Any,
) -> List[Dict[str, Any]]:
    merged = list(current)
    if policy_rules:
        if not isinstance(policy_rules, list):
            raise ValueError("Policy custom_rules must be a list")
        merged.extend(policy_rules)
    if override_rules:
        if not isinstance(override_rules, list):
            raise ValueError("Policy overrides custom_rules must be a list")
        merged.extend(override_rules)
    return merged
