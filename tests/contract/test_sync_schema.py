import json
import os
import pytest
from jsonschema import validate, ValidationError


def test_sync_schema_contract():
    schema_path = os.path.join(os.path.dirname(__file__), "../../specs/002-academic-sentinel/contracts/sync-schema.json")
    assert os.path.exists(schema_path)

    with open(schema_path, "r") as f:
        schema = json.load(f)

    valid_payload = {
        "student_id": "student_123",
        "synced_at": "2026-08-20T17:00:00Z",
        "courses_processed": 1,
        "missing_assignments_evaluated": 2,
        "alerts_dispatched": [
            {
                "alert_type": "MISSING_WORK",
                "priority": "P0",
                "dispatched_at": "2026-08-20T17:00:01Z"
            }
        ]
    }

    # Should not raise ValidationError
    validate(instance=valid_payload, schema=schema)



def test_sync_schema_missing_required_field():
    schema_path = os.path.join(os.path.dirname(__file__), "../../specs/002-academic-sentinel/contracts/sync-schema.json")
    with open(schema_path, "r") as f:
        schema = json.load(f)

    invalid_payload = {
        "student_id": "student_123",
        "courses_processed": 1
    }

    with pytest.raises(ValidationError):
        validate(instance=invalid_payload, schema=schema)

