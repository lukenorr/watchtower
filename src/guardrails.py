# setup the expected structure from the triage result
TRIAGE_SCHEMA = {
    "domain" : {"type": str, "required": True},
    "verdict" : {"type": str, "allowed":("benign", "suspicious", "malicious", "unknown")},
    "severity" : {"type": str, "allowed":("low", "medium", "high")},
    "confidence" : {"type": (int, float), "min": 0.0, "max": 1.0},
    "reasoning" : {"type": str, "required": True}
}

def validate_schema(triage_result):
    """
    Validate triage result against expected schema
    Input: triage result dict (see schema above)
    Output: list of error strings; empty if valid
    Checks: type, bounds, allowed values, required fields
    """
    # loop through each field and check
    errors = []
    for field, constraints in TRIAGE_SCHEMA.items():
        value = triage_result.get(field)
        if value is None:
            errors.append(f"missing '{field}'")
            continue
        # check type
        if not isinstance(value, constraints.get("type")):
            errors.append(f"invalid type={type(value)}, expected={constraints.get('type')}")
            continue
        # check number is within bounds
        if isinstance(value, (int, float)):
            field_min = constraints.get("min")
            field_max = constraints.get("max")
            if not (value >= field_min and value <= field_max):
                errors.append(f"{field} {value} is outside numerical bounds [{field_min}, {field_max}]")
                continue
        # check if required
        if constraints.get("required") and isinstance(value, str) and len(value.strip())==0:
            errors.append("string required")
            continue
        # check in allowed list
        if constraints.get("allowed"):
            if value not in constraints.get("allowed"):
                errors.append(f"{value} not in allowed schema values")
                continue
    return errors

def validate_domain(triage_result, event):
    """
    Check the LLM analysed correct domain
    Input: triage result dict (see schema at top); parsed event log dict
    Output: list of error strings; empty if valid
    Checks: normalisation- lowercase, trailing dot
    """
    errors = []
    triage_domain = triage_result.get("domain").rstrip(".").lower()
    event_domain = event.get("domain").rstrip(".").lower()
    if triage_domain != event_domain:
        errors.append(f"triage domain ({triage_domain}) not the same as event domain ({event_domain})")
    return errors

if __name__ == "__main__":
    sample_result_1 = {
        "domain" : "github.ru",
        "verdict" : "suspicious", 
        "severity" : "low",
        "confidence" : 5.2,
        "reasoning" : f"JSON parse failed. Raw response: 123"
    }
    sample_result_2 = {
        "domain" : "bbc.virus",
        "verdict" : "malicious", 
        "severity" : "high",
        "confidence" : 0.5,
        "reasoning" : f"JSON parse failed. Raw response: 123"
    }
    sample_result_3 = {
        "domain" : "github.com.",
        "verdict" : "suspicious", 
        "severity" : "high",
        "confidence" : 0.5,
        "reasoning" : f"JSON parse failed. Raw response: 123"
    }
    event_result_1 = {
        "timestamp": "2026-06-27T20:15:01",
        "source" : "pihole",
        "log_type" : "dns_query",
        "domain" : "github.com",
        "client_ip" : "128.0.01.68",
        "query_type" : "AAA",
        "raw_log" : "unknown",
    }

    errors = validate_schema(sample_result_1)
    assert len(errors) > 0, "should catch out-of-range confidence"
    errors = validate_schema(sample_result_2)
    assert len(errors) == 0, f"should be clean, got {errors}"
    errors = validate_domain(sample_result_3, event_result_1)
    assert len(errors) == 0, f"should be clean, got {errors}"
    errors = validate_domain(sample_result_1, event_result_1)
    assert len(errors) > 0, "should catch domain mismatch"
    print("All schema validation tests passed.")       