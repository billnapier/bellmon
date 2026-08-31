# Quickstart: Phase 1.8 Daily Heartbeat & System Activity Briefing

## Running the Heartbeat Generator

```python
from src.notifications.heartbeat import HeartbeatBriefingGenerator
from src.storage.firestore import FirestoreStateEngine

# Initialize generator
engine = FirestoreStateEngine()
generator = HeartbeatBriefingGenerator(db_client=engine)

# Collect telemetry and dispatch briefing
result = generator.generate_and_dispatch(
    student_id="student_123",
    recipient_email="parent@example.com",
    student_name="Alex Napier",
    date="2026-08-31"
)

print(f"Dispatch status: {result.success}, Message ID: {result.message_id}")
```

## Testing

```bash
pytest tests/test_heartbeat.py -v
```
