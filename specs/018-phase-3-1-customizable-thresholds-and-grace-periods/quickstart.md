# Quickstart: Phase 3.1 Customizable Notification Thresholds and Grace Periods

## Running Tests

Execute the full test suite including custom preferences verification:

```bash
.venv/bin/pytest tests/test_custom_preferences.py
.venv/bin/pytest
```

## Example Usage in Code

```python
from src.storage.models import StudentPreferences
from src.storage.firestore import FirestoreStateEngine

# Initialize custom preferences for a student
prefs = StudentPreferences(
    grace_period_hours=24,
    velocity_drop_threshold=2.5,
    late_submission_threshold=2,
    workload_clumping_threshold=3,
    workload_clumping_window_hours=72,
    weekend_grace_pause=True
)

# Persist to Firestore
engine = FirestoreStateEngine()
engine.update_student_preferences("student_123", prefs)
```
