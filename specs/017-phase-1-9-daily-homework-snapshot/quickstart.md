# Quickstart: Phase 1.9 Daily Evening Homework & Deadline Snapshot

## Running Homework Snapshot Generator

```python
from datetime import datetime, timezone
from src.notifications.homework_snapshot import HomeworkSnapshotGenerator

generator = HomeworkSnapshotGenerator()

# Generate and dispatch snapshot
result = generator.generate_and_dispatch(
    student_id="student_123",
    recipient_email="parent@example.com",
    student_name="Alex",
    snapshot_time=datetime.now(timezone.utc)
)

print(f"Dispatch status: {result.status}, email_id: {result.email_id}")
```

## Testing

Run unit tests:
```bash
.venv/bin/pytest tests/test_homework_snapshot.py
```
