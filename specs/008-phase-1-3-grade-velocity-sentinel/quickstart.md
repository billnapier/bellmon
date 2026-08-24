# Quickstart: Phase 1.3 Grade Velocity Drop Sentinel

## Overview

The `GradeVelocityEngine` evaluates rolling grade velocity drop alerts ($\ge 4.0\%$) over a $[t-10, t-7]$ day baseline window, enforcing early-term noise suppression and a 7-day silent warming protocol.

## Running Tests

To verify the implementation:

```bash
/home/napier/a/bellmon/.venv/bin/pytest tests/test_velocity.py -v
```

To run the complete test suite:

```bash
/home/napier/a/bellmon/.venv/bin/pytest -v
```

## Basic Usage Example

```python
from datetime import date
from src.engine.models import CourseVelocityInput, StudentVelocityContext
from src.engine.velocity import GradeVelocityEngine
from src.storage.models import GradeSnapshot

engine = GradeVelocityEngine()

context = StudentVelocityContext(
    student_id="student_123",
    tracking_start_date="2026-08-01",  # > 7 days prior to eval_date
    courses=[
        CourseVelocityInput(
            course_id="course_algebra",
            course_name="Algebra II",
            current_percentage=88.0,
            total_graded_points=150.0,
            term_active_days=25,
            history=[
                GradeSnapshot(date="2026-08-14", percentage=93.0, letter_grade="A"), # 7 days ago
            ]
        )
    ]
)

alerts = engine.evaluate_student_velocity(
    student_context=context,
    eval_date=date(2026, 8, 21),
)

print(f"Triggered Alerts: {len(alerts)}")
# Output: Triggered Alerts: 1 (Delta = 5.0% >= 4.0%)
```
