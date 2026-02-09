"""Sample custom rules for tests."""


def field_max_value(series, config, field, df):
    limit = config.get("value") if isinstance(config, dict) else None
    if limit is None:
        return True, ""
    violations = (series > limit).sum()
    if violations > 0:
        return False, f"Field '{field.name}' has {violations} values > {limit}"
    return True, ""


def dataset_min_rows(df, config):
    minimum = config.get("value") if isinstance(config, dict) else None
    if minimum is None:
        return True, ""
    if len(df) < minimum:
        return False, f"Dataset has {len(df)} rows, expected at least {minimum}"
    return True, ""


RULES = {
    "field_max_value": field_max_value,
    "dataset_min_rows": dataset_min_rows,
}
