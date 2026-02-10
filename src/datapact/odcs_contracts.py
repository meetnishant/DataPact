"""
ODCS (Open Data Contract Standard) contract parsing and mapping.
Provides a lightweight parser and a mapper to DataPact Contract for validation.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from datapact.contracts import (
    Contract,
    Dataset,
    Field,
    FieldRule,
    SchemaPolicy,
    SLA,
)


@dataclass
class OdcsQualityRule:
    rule_id: Optional[str]
    name: Optional[str]
    description: Optional[str]
    rule_type: Optional[str]
    metric: Optional[str]
    arguments: Dict[str, Any]
    query: Optional[str]
    engine: Optional[str]
    implementation: Optional[str]
    dimension: Optional[str]
    severity: Optional[str]
    business_impact: Optional[str]
    schedule: Optional[str]
    scheduler: Optional[str]
    unit: Optional[str]
    operators: Dict[str, Any] = field(default_factory=dict)
    tags: List[Any] = field(default_factory=list)
    custom_properties: List[Dict[str, Any]] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OdcsSchemaProperty:
    name: str
    logical_type: Optional[str]
    physical_type: Optional[str]
    required: bool
    unique: bool
    quality: List[OdcsQualityRule]
    tags: List[Any] = field(default_factory=list)
    classification: Optional[str] = None
    logical_type_options: Dict[str, Any] = field(default_factory=dict)
    custom_properties: List[Dict[str, Any]] = field(default_factory=list)
    authoritative_definitions: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    transform_source_objects: List[str] = field(default_factory=list)
    transform_logic: Optional[str] = None
    transform_description: Optional[str] = None
    examples: List[Any] = field(default_factory=list)
    critical_data_element: Optional[bool] = None
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OdcsSchemaObject:
    name: str
    object_id: Optional[str]
    description: Optional[str]
    properties: List[OdcsSchemaProperty]
    quality: List[OdcsQualityRule]
    tags: List[Any] = field(default_factory=list)
    custom_properties: List[Dict[str, Any]] = field(default_factory=list)
    authoritative_definitions: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OdcsSlaProperty:
    sla_id: Optional[str]
    property: Optional[str]
    value: Any
    unit: Optional[str]
    element: Optional[str]
    driver: Optional[str]
    schedule: Optional[str]
    scheduler: Optional[str]
    description: Optional[str]
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OdcsContract:
    api_version: str
    kind: str
    contract_id: str
    name: Optional[str]
    version: str
    status: str
    tenant: Optional[str]
    domain: Optional[str]
    data_product: Optional[str]
    description: Dict[str, Any]
    tags: List[Any]
    authoritative_definitions: List[Dict[str, Any]]
    custom_properties: List[Dict[str, Any]]
    contract_created_ts: Optional[str]
    schema: List[OdcsSchemaObject]
    quality: List[OdcsQualityRule]
    sla_properties: List[OdcsSlaProperty]
    servers: List[Dict[str, Any]]
    roles: List[Dict[str, Any]]
    team: Dict[str, Any]
    support: List[Dict[str, Any]]
    price: Optional[Dict[str, Any]]
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OdcsContract":
        if not isinstance(data, dict):
            raise ValueError("ODCS contract must be a mapping")

        api_version = _require_str(data, "apiVersion")
        kind = _require_str(data, "kind")
        contract_id = _require_str(data, "id")
        version = _require_str(data, "version")
        status = _require_str(data, "status")

        schema = [_parse_schema_object(obj) for obj in _list(data, "schema")]
        quality = [_parse_quality_rule(rule) for rule in _list(data, "quality")]
        sla_properties = [
            _parse_sla_property(item) for item in _list(data, "slaProperties")
        ]

        return cls(
            api_version=api_version,
            kind=kind,
            contract_id=contract_id,
            name=_optional_str(data, "name"),
            version=version,
            status=status,
            tenant=_optional_str(data, "tenant"),
            domain=_optional_str(data, "domain"),
            data_product=_optional_str(data, "dataProduct"),
            description=_dict(data, "description"),
            tags=_list(data, "tags"),
            authoritative_definitions=_list(data, "authoritativeDefinitions"),
            custom_properties=_list(data, "customProperties"),
            contract_created_ts=_optional_str(data, "contractCreatedTs"),
            schema=schema,
            quality=quality,
            sla_properties=sla_properties,
            servers=_list(data, "servers"),
            roles=_list(data, "roles"),
            team=_dict(data, "team"),
            support=_list(data, "support"),
            price=_dict_or_none(data, "price"),
            raw=data,
        )

    def get_schema_object(self, name_or_id: Optional[str]) -> OdcsSchemaObject:
        if not self.schema:
            raise ValueError("ODCS contract has no schema objects")

        if not name_or_id:
            if len(self.schema) == 1:
                return self.schema[0]
            raise ValueError(
                "ODCS contract has multiple schema objects; "
                "use --odcs-object to select one"
            )

        for obj in self.schema:
            if obj.name == name_or_id or obj.object_id == name_or_id:
                return obj

        raise ValueError(f"ODCS schema object '{name_or_id}' not found")

    def to_datapact_contract(
        self, object_name: Optional[str] = None
    ) -> Tuple[Contract, List[str], Dict[str, Any]]:
        obj = self.get_schema_object(object_name)
        warnings: List[str] = []

        fields: List[Field] = []
        for prop in obj.properties:
            field_rules = FieldRule()

            if prop.required:
                field_rules.not_null = True
                field_rules.severities.setdefault("not_null", "ERROR")

            if prop.unique:
                field_rules.unique = True
                field_rules.severities.setdefault("unique", "ERROR")

            mapped_rules, rule_warnings = _map_quality_rules(prop.quality)
            warnings.extend(rule_warnings)
            field_rules = _merge_rules(field_rules, mapped_rules)

            field_type, type_warnings = _map_logical_type(prop.logical_type)
            warnings.extend(type_warnings)

            fields.append(
                Field(
                    name=prop.name,
                    type=field_type,
                    required=False,
                    rules=field_rules if _has_rules(field_rules) else None,
                    distribution=None,
                )
            )

        sla = SLA()
        sla_warnings: List[str] = []
        obj_quality = obj.quality + self.quality
        sla, sla_warnings = _map_rowcount_quality(obj_quality)
        warnings.extend(sla_warnings)

        contract = Contract(
            name=self.name or obj.name or self.contract_id,
            version=self.version,
            dataset=Dataset(name=obj.name),
            fields=fields,
            schema_policy=SchemaPolicy(),
            sla=sla,
            custom_rules=[],
        )

        odcs_metadata = _build_odcs_metadata(self.raw)
        warnings.extend(_metadata_warnings(self.raw))
        return contract, warnings, odcs_metadata


def is_odcs_contract(data: Dict[str, Any]) -> bool:
    return isinstance(data, dict) and "apiVersion" in data and "kind" in data


def _parse_schema_object(data: Dict[str, Any]) -> OdcsSchemaObject:
    if not isinstance(data, dict):
        raise ValueError("ODCS schema object must be a mapping")

    name = _require_str(data, "name")
    properties = [
        _parse_schema_property(prop) for prop in _list(data, "properties")
    ]
    quality = [_parse_quality_rule(rule) for rule in _list(data, "quality")]

    return OdcsSchemaObject(
        name=name,
        object_id=_optional_str(data, "id"),
        description=_optional_str(data, "description"),
        properties=properties,
        quality=quality,
        tags=_list(data, "tags"),
        custom_properties=_list(data, "customProperties"),
        authoritative_definitions=_list(data, "authoritativeDefinitions"),
        relationships=_list(data, "relationships"),
        raw=data,
    )


def _parse_schema_property(data: Dict[str, Any]) -> OdcsSchemaProperty:
    if not isinstance(data, dict):
        raise ValueError("ODCS schema property must be a mapping")

    name = _require_str(data, "name")
    quality = [_parse_quality_rule(rule) for rule in _list(data, "quality")]

    return OdcsSchemaProperty(
        name=name,
        logical_type=_optional_str(data, "logicalType"),
        physical_type=_optional_str(data, "physicalType"),
        required=bool(data.get("required", False)),
        unique=bool(data.get("unique", False)),
        quality=quality,
        tags=_list(data, "tags"),
        classification=_optional_str(data, "classification"),
        logical_type_options=_dict(data, "logicalTypeOptions"),
        custom_properties=_list(data, "customProperties"),
        authoritative_definitions=_list(data, "authoritativeDefinitions"),
        relationships=_list(data, "relationships"),
        transform_source_objects=_list(data, "transformSourceObjects"),
        transform_logic=_optional_str(data, "transformLogic"),
        transform_description=_optional_str(data, "transformDescription"),
        examples=_list(data, "examples"),
        critical_data_element=data.get("criticalDataElement"),
        raw=data,
    )


def _parse_quality_rule(data: Dict[str, Any]) -> OdcsQualityRule:
    if not isinstance(data, dict):
        raise ValueError("ODCS quality rule must be a mapping")

    operators = {
        key: value for key, value in data.items() if key.startswith("must")
    }

    return OdcsQualityRule(
        rule_id=_optional_str(data, "id"),
        name=_optional_str(data, "name"),
        description=_optional_str(data, "description"),
        rule_type=_optional_str(data, "type"),
        metric=_optional_str(data, "metric"),
        arguments=_dict(data, "arguments"),
        query=_optional_str(data, "query"),
        engine=_optional_str(data, "engine"),
        implementation=_optional_str(data, "implementation"),
        dimension=_optional_str(data, "dimension"),
        severity=_optional_str(data, "severity"),
        business_impact=_optional_str(data, "businessImpact"),
        schedule=_optional_str(data, "schedule"),
        scheduler=_optional_str(data, "scheduler"),
        unit=_optional_str(data, "unit"),
        operators=operators,
        tags=_list(data, "tags"),
        custom_properties=_list(data, "customProperties"),
        raw=data,
    )


def _parse_sla_property(data: Dict[str, Any]) -> OdcsSlaProperty:
    if not isinstance(data, dict):
        raise ValueError("ODCS SLA property must be a mapping")

    return OdcsSlaProperty(
        sla_id=_optional_str(data, "id"),
        property=_optional_str(data, "property"),
        value=data.get("value"),
        unit=_optional_str(data, "unit"),
        element=_optional_str(data, "element"),
        driver=_optional_str(data, "driver"),
        schedule=_optional_str(data, "schedule"),
        scheduler=_optional_str(data, "scheduler"),
        description=_optional_str(data, "description"),
        raw=data,
    )


def _map_logical_type(logical_type: Optional[str]) -> Tuple[str, List[str]]:
    if not logical_type:
        return "string", []

    normalized = str(logical_type).lower()
    mapping = {
        "integer": "integer",
        "number": "float",
        "boolean": "boolean",
        "string": "string",
        "date": "string",
        "timestamp": "string",
        "time": "string",
    }
    if normalized in {"date", "time", "timestamp"}:
        return "string", [
            f"WARN: ODCS logicalType '{logical_type}' mapped to string"
        ]
    if normalized in mapping:
        return mapping[normalized], []
    return "string", [f"WARN: ODCS logicalType '{logical_type}' mapped to string"]


def _map_quality_rules(
    rules: List[OdcsQualityRule],
) -> Tuple[FieldRule, List[str]]:
    warnings: List[str] = []
    field_rules = FieldRule()

    for rule in rules:
        if rule.rule_type and rule.rule_type not in {"library", "text"}:
            warnings.append(
                f"WARN: ODCS quality rule '{rule.rule_id or rule.name}' "
                f"type '{rule.rule_type}' not executed"
            )
            continue

        metric = (rule.metric or "").lower()
        if metric in {"nullvalues", "missingvalues"}:
            if _is_zero_operator(rule.operators):
                field_rules.not_null = True
                _apply_severity(field_rules, "not_null", rule.severity)
            else:
                max_ratio = _operator_to_ratio(rule.operators, rule.unit)
                if max_ratio is not None:
                    field_rules.max_null_ratio = max_ratio
                    _apply_severity(field_rules, "max_null_ratio", rule.severity)
                else:
                    warnings.append(
                        f"WARN: ODCS null metric '{rule.rule_id or rule.name}' "
                        "not mapped to DataPact"
                    )
        elif metric == "duplicatevalues":
            if _is_zero_operator(rule.operators):
                field_rules.unique = True
                _apply_severity(field_rules, "unique", rule.severity)
            else:
                warnings.append(
                    f"WARN: ODCS duplicate metric '{rule.rule_id or rule.name}' "
                    "not mapped to DataPact"
                )
        elif metric in {"invalidvalues", "rowcount"}:
            warnings.append(
                f"WARN: ODCS metric '{metric}' not mapped to DataPact field rules"
            )
        elif rule.metric:
            warnings.append(
                f"WARN: ODCS metric '{rule.metric}' not mapped to DataPact"
            )

    return field_rules, warnings


def _map_rowcount_quality(
    rules: List[OdcsQualityRule],
) -> Tuple[SLA, List[str]]:
    sla = SLA()
    warnings: List[str] = []

    for rule in rules:
        metric = (rule.metric or "").lower()
        if metric != "rowcount":
            continue

        ops = rule.operators
        if "mustBeBetween" in ops and isinstance(ops["mustBeBetween"], list):
            bounds = ops["mustBeBetween"]
            if len(bounds) == 2:
                sla.min_rows = int(bounds[0])
                sla.max_rows = int(bounds[1])
        if "mustBeGreaterThan" in ops:
            sla.min_rows = int(ops["mustBeGreaterThan"]) + 1
        if "mustBeGreaterThanOrEqualTo" in ops:
            sla.min_rows = int(ops["mustBeGreaterThanOrEqualTo"])
        if "mustBeLessThan" in ops:
            sla.max_rows = int(ops["mustBeLessThan"]) - 1
        if "mustBeLessThanOrEqualTo" in ops:
            sla.max_rows = int(ops["mustBeLessThanOrEqualTo"])
        if "mustBe" in ops:
            value = int(ops["mustBe"])
            sla.min_rows = value
            sla.max_rows = value

        _apply_sla_severity(sla, rule.severity)

    if sla.min_rows is None and sla.max_rows is None:
        return SLA(), warnings

    return sla, warnings


def _apply_severity(rules: FieldRule, rule_name: str, severity: Optional[str]) -> None:
    if not severity:
        return
    normalized = str(severity).upper()
    if normalized in {"ERROR", "WARN"}:
        rules.severities[rule_name] = normalized


def _apply_sla_severity(sla: SLA, severity: Optional[str]) -> None:
    if not severity:
        return
    normalized = str(severity).upper()
    if normalized not in {"ERROR", "WARN"}:
        return
    if sla.min_rows is not None:
        sla.min_rows_severity = normalized
    if sla.max_rows is not None:
        sla.max_rows_severity = normalized


def _merge_rules(base: FieldRule, extra: FieldRule) -> FieldRule:
    base.not_null = base.not_null or extra.not_null
    base.unique = base.unique or extra.unique
    base.min = base.min if base.min is not None else extra.min
    base.max = base.max if base.max is not None else extra.max
    base.regex = base.regex or extra.regex
    base.enum = base.enum or extra.enum
    base.max_null_ratio = (
        base.max_null_ratio
        if base.max_null_ratio is not None
        else extra.max_null_ratio
    )
    base.freshness_max_age_hours = (
        base.freshness_max_age_hours
        if base.freshness_max_age_hours is not None
        else extra.freshness_max_age_hours
    )
    base.custom.update(extra.custom)
    base.severities.update(extra.severities)
    return base


def _has_rules(rules: FieldRule) -> bool:
    return any(
        [
            rules.not_null,
            rules.unique,
            rules.min is not None,
            rules.max is not None,
            rules.regex is not None,
            rules.enum is not None,
            rules.max_null_ratio is not None,
            rules.freshness_max_age_hours is not None,
            bool(rules.custom),
        ]
    )


def _operator_to_ratio(operators: Dict[str, Any], unit: Optional[str]) -> Optional[float]:
    if "mustBe" in operators:
        return _ratio_from_value(operators["mustBe"], unit)
    if "mustBeLessThan" in operators:
        return _ratio_from_value(operators["mustBeLessThan"], unit)
    if "mustBeLessThanOrEqualTo" in operators:
        return _ratio_from_value(operators["mustBeLessThanOrEqualTo"], unit)
    return None


def _ratio_from_value(value: Any, unit: Optional[str]) -> Optional[float]:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None

    if unit and str(unit).lower() in {"percent", "%"}:
        return numeric / 100.0
    if numeric > 1:
        return None
    return numeric


def _is_zero_operator(operators: Dict[str, Any]) -> bool:
    return any(
        operators.get(key) == 0 for key in ("mustBe", "mustBeLessThanOrEqualTo")
    )


def _metadata_warnings(raw: Dict[str, Any]) -> List[str]:
    warnings: List[str] = []
    if "servers" in raw and not raw.get("servers"):
        warnings.append("WARN: ODCS servers section is empty")
    if "team" in raw and not raw.get("team"):
        warnings.append("WARN: ODCS team section is empty")
    return warnings


def _build_odcs_metadata(raw: Dict[str, Any]) -> Dict[str, Any]:
    metadata_keys = [
        "apiVersion",
        "kind",
        "id",
        "name",
        "version",
        "status",
        "tenant",
        "domain",
        "dataProduct",
        "description",
        "tags",
        "authoritativeDefinitions",
        "customProperties",
        "contractCreatedTs",
        "schema",
        "quality",
        "slaProperties",
        "servers",
        "roles",
        "team",
        "support",
        "price",
    ]
    return {key: raw.get(key) for key in metadata_keys if key in raw}


def _require_str(data: Dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"ODCS contract requires '{key}'")
    return value


def _optional_str(data: Dict[str, Any], key: str) -> Optional[str]:
    value = data.get(key)
    if value is None:
        return None
    return str(value)


def _list(data: Dict[str, Any], key: str) -> List[Any]:
    value = data.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"ODCS '{key}' must be a list")
    return value


def _dict(data: Dict[str, Any], key: str) -> Dict[str, Any]:
    value = data.get(key)
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"ODCS '{key}' must be a mapping")
    return value


def _dict_or_none(data: Dict[str, Any], key: str) -> Optional[Dict[str, Any]]:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError(f"ODCS '{key}' must be a mapping")
    return value
