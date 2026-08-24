# Quickstart Guide: 011 Phase 2.1 Workload Clumping Radar

## Running Workload Radar Evaluation

```python
from datetime import datetime, timezone
from src.radar.engine import WorkloadRadarEngine

engine = WorkloadRadarEngine()

raw_assignments = [
    {
        "id": "101",
        "title": "AP Chemistry Unit 4 Exam",
        "course_name": "AP Chemistry",
        "due_at": "2026-08-26T14:00:00Z",
        "points_possible": 100.0,
        "category": "Exams",
        "has_submitted": False,
    },
    {
        "id": "102",
        "title": "English Literature Research Paper",
        "course_name": "English Lit",
        "due_at": "2026-08-27T10:00:00Z",
        "points_possible": 50.0,
        "category": "Essays",
        "has_submitted": False,
    }
]

now = datetime(2026, 8, 25, 8, 0, tzinfo=timezone.utc)
result = engine.evaluate(raw_assignments, now=now)

print(f"Clumping Detected: {result.has_clumping}")
for cluster in result.clusters:
    print(f"Cluster: {cluster.courses} ({len(cluster.assessments)} major items)")
```

## Running Unit Tests

```bash
pytest tests/test_workload_radar.py -v
```
