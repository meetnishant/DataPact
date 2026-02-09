from datapact.contracts import Contract


def test_policy_pack_applies_rules():
    contract = Contract.from_yaml("tests/fixtures/policy_pack_contract.yaml")
    field_map = {field.name: field for field in contract.fields}

    email_rules = field_map["email"].rules
    assert email_rules is not None
    assert email_rules.not_null is True
    assert email_rules.unique is True
    assert email_rules.regex is not None


def test_policy_pack_overrides_rule():
    contract = Contract.from_yaml("tests/fixtures/policy_pack_contract.yaml")
    field_map = {field.name: field for field in contract.fields}

    phone_rules = field_map["phone"].rules
    assert phone_rules is not None
    assert phone_rules.regex == "^\\+1[0-9]{10}$"
    assert phone_rules.severities.get("regex") == "WARN"
