# Quickstart: Phase 1.4 Period Attendance Anomaly Sentinel

## Overview

This module provides the `AttendanceSentinel` class to detect P0 unexcused absences and cuts, deduplicate alerts against Firestore ledger history, and queue minor codes (tardies/unverified) for Sunday digest.

## Running Tests

Run the dedicated pytest suite:

```bash
pytest tests/test_attendance.py -v
```

## Basic Usage Example

```python
from src.engine.attendance import AttendanceSentinel
from src.engine.models import AttendanceRecordInput, AttendanceEvent

sentinel = AttendanceSentinel()

raw_records = [
    AttendanceRecordInput(
        date="2026-08-24",
        period=2,
        course_name="Algebra II",
        code="A",
        description="Unexcused Absence"
    ),
    AttendanceRecordInput(
        date="2026-08-24",
        period=4,
        course_name="Chemistry",
        code="T",
        description="Tardy"
    )
]

existing_events = []

alerts, updated_events = sentinel.evaluate_student_attendance(
    student_id="student_123",
    records=raw_records,
    existing_events=existing_events
)

# alerts contains 1 PendingAttendanceAlert for Algebra II (P0)
# updated_events contains 2 AttendanceEvent records (Algebra II notified=True, Chemistry notified=False)
```
