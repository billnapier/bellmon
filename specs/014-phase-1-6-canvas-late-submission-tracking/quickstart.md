# Quickstart & Verification: Phase 1.6 Canvas Late Submission Tracking

## Testing Strategy

Run pytest on late submission unit & integration tests:
```bash
pytest tests/test_canvas_late_submissions.py -v
```

## Example Usage

```python
from src.ingestion.canvas import CanvasClient
from src.storage.firestore import FirestoreStateEngine

engine = FirestoreStateEngine(use_mock=True)

# Ingest late submission payload
late_records = engine.save_late_submissions("student_123", raw_submissions)

# Query late submissions within date window
records = engine.get_late_submissions("student_123", start_date="2026-08-01", end_date="2026-08-31")
```
