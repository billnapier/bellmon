# Quickstart Guide: 012 Phase 2.2 Sunday Planning Digest

## Rendering Sunday Digest Email

```python
from datetime import datetime, timezone
from src.notifications.digest import SundayDigestPayload, SundayDigestRenderer
from src.radar.models import WorkloadRadarResult

payload = SundayDigestPayload(
    student_name="Alex Smith",
    digest_date=datetime.now(timezone.utc),
    course_standings=[
        {"course_name": "AP Physics", "grade_letter": "A", "grade_percent": 94.5, "teacher_name": "Dr. Vance"},
        {"course_name": "Calculus BC", "grade_letter": "B+", "grade_percent": 88.0, "teacher_name": "Mr. Euler"},
    ],
    workload_radar=WorkloadRadarResult(has_clumping=False, evaluated_at=datetime.now(timezone.utc), clusters=[]),
    upcoming_deadlines=[
        {"title": "Chapter 5 Quiz", "course_name": "Calculus BC", "due_at": "2026-08-26T14:00:00Z", "points_possible": 30.0}
    ],
    attendance_records=[],
    tardy_count=1,
    unverified_count=0,
)

renderer = SundayDigestRenderer()
html_output = renderer.render_html(payload)
text_output = renderer.render_text(payload)

print(f"Generated HTML size: {len(html_output)} bytes")
```

## Running Unit Tests

```bash
.venv/bin/pytest tests/test_sunday_digest.py -v
```
