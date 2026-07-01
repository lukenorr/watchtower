
def validate_schema(triage_result):
    # setup the expected structure from the triage result
    structure = {
        "verdict" : {"type": str, "allowed":("benign", "suspicious", "malicious", "unknown")},
        "severity" : {"type": str, "allowed":("low", "medium", "high")},
        "confidence" : {"type": (int, float), "min": 0.0, "max": 1.0},
        "reasoning" : {"type": str, "required": True}
    }

    # loop through each field and check
    errors = []
    for field, constraints in structure.items():
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
                errors.append(f"outside numberical bounds")
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

if __name__ == "__main__":
    sample_result_1 = {
        "verdict" : "suspicious", 
        "severity" : "low",
        "confidence" : 5.2,
        "reasoning" : f"JSON parse failed. Raw response: 123"
    }
    sample_result_2 = {
        "verdict" : "malicious", 
        "severity" : "high",
        "confidence" : 0.5,
        "reasoning" : f"JSON parse failed. Raw response: 123"
    }
    errors = validate_schema(sample_result_1)
    assert len(errors) > 0, "should catch out-of-range confidence"
    errors = validate_schema(sample_result_2)
    assert len(errors) == 0, f"should be clean, got {errors}"       