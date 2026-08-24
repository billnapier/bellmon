"""
Unit tests for AttendanceSentinel (Phase 1.4 Period Attendance Anomaly Sentinel).
"""

from datetime import datetime, timezone
import pytest
from src.engine.attendance import AttendanceSentinel
from src.engine.models import (
    AttendanceCodeSeverity,
    AttendanceRecordInput,
    AttendanceEvent,
    PendingAttendanceAlert,
)


def test_classify_code():
    sentinel = AttendanceSentinel()
    assert sentinel.classify_code("A") == AttendanceCodeSeverity.P0_URGENT
    assert sentinel.classify_code("CUT") == AttendanceCodeSeverity.P0_URGENT
    assert sentinel.classify_code("a ") == AttendanceCodeSeverity.P0_URGENT
    assert sentinel.classify_code("cut") == AttendanceCodeSeverity.P0_URGENT

    assert sentinel.classify_code("T") == AttendanceCodeSeverity.P1_DIGEST
    assert sentinel.classify_code("U") == AttendanceCodeSeverity.P1_DIGEST
    assert sentinel.classify_code("t") == AttendanceCodeSeverity.P1_DIGEST

    assert sentinel.classify_code("P") == AttendanceCodeSeverity.IGNORED
    assert sentinel.classify_code("E") == AttendanceCodeSeverity.IGNORED
    assert sentinel.classify_code("EX") == AttendanceCodeSeverity.IGNORED
    assert sentinel.classify_code("ACT") == AttendanceCodeSeverity.IGNORED
    assert sentinel.classify_code("") == AttendanceCodeSeverity.IGNORED
    assert sentinel.classify_code("xyz") == AttendanceCodeSeverity.IGNORED


def test_evaluate_p0_absence_and_cut():
    sentinel = AttendanceSentinel()
    now = datetime(2026, 8, 24, 10, 0, 0, tzinfo=timezone.utc)

    records = [
        AttendanceRecordInput(
            date="2026-08-24",
            period=2,
            course_name="Algebra II",
            code="A",
        ),
        AttendanceRecordInput(
            date="2026-08-24",
            period=4,
            course_name="Chemistry",
            code="CUT",
            description="Skipped class",
        ),
    ]

    alerts, updated_events = sentinel.evaluate_student_attendance(
        student_id="student_001",
        records=records,
        existing_events=[],
        now=now,
    )

    assert len(alerts) == 2
    assert alerts[0].student_id == "student_001"
    assert alerts[0].date == "2026-08-24"
    assert alerts[0].period == 2
    assert alerts[0].course_name == "Algebra II"
    assert alerts[0].code == "A"
    assert alerts[0].description == "Unexcused Absence"
    assert alerts[0].severity == AttendanceCodeSeverity.P0_URGENT

    assert alerts[1].period == 4
    assert alerts[1].code == "CUT"
    assert alerts[1].description == "Skipped class"

    assert len(updated_events) == 2
    for ev in updated_events:
        assert ev.notified is True
        assert ev.severity == AttendanceCodeSeverity.P0_URGENT


def test_evaluate_ignored_codes_produces_no_alerts():
    sentinel = AttendanceSentinel()
    records = [
        AttendanceRecordInput(
            date="2026-08-24",
            period=1,
            course_name="English",
            code="P",
        ),
        AttendanceRecordInput(
            date="2026-08-24",
            period=3,
            course_name="History",
            code="E",
        ),
        AttendanceRecordInput(
            date="2026-08-24",
            period=5,
            course_name="Physics",
            code="ACT",
        ),
    ]

    alerts, updated_events = sentinel.evaluate_student_attendance(
        student_id="student_001",
        records=records,
        existing_events=[],
    )

    assert len(alerts) == 0
    assert len(updated_events) == 0


def test_alert_deduplication():
    sentinel = AttendanceSentinel()
    now = datetime(2026, 8, 24, 12, 0, 0, tzinfo=timezone.utc)

    # Pre-existing event already notified
    existing_event = AttendanceEvent(
        date="2026-08-24",
        period=2,
        course_name="Algebra II",
        code="A",
        description="Unexcused Absence",
        severity=AttendanceCodeSeverity.P0_URGENT,
        notified=True,
        detected_at="2026-08-24T09:00:00+00:00",
    )

    records = [
        AttendanceRecordInput(
            date="2026-08-24",
            period=2,
            course_name="Algebra II",
            code="A",
        )
    ]

    alerts, updated_events = sentinel.evaluate_student_attendance(
        student_id="student_001",
        records=records,
        existing_events=[existing_event],
        now=now,
    )

    # Alert generation should be suppressed
    assert len(alerts) == 0
    assert len(updated_events) == 1
    assert updated_events[0].notified is True


def test_minor_attendance_code_queuing():
    sentinel = AttendanceSentinel()
    now = datetime(2026, 8, 24, 14, 0, 0, tzinfo=timezone.utc)

    records = [
        AttendanceRecordInput(
            date="2026-08-24",
            period=1,
            course_name="Spanish",
            code="T",
        ),
        AttendanceRecordInput(
            date="2026-08-24",
            period=3,
            course_name="Biology",
            code="U",
        ),
    ]

    alerts, updated_events = sentinel.evaluate_student_attendance(
        student_id="student_001",
        records=records,
        existing_events=[],
        now=now,
    )

    # P0 alerts must be zero
    assert len(alerts) == 0
    assert len(updated_events) == 2

    # Events stored with notified=False and severity=P1_DIGEST
    tardy_event = next(e for e in updated_events if e.period == 1)
    assert tardy_event.code == "T"
    assert tardy_event.severity == AttendanceCodeSeverity.P1_DIGEST
    assert tardy_event.notified is False

    unverified_event = next(e for e in updated_events if e.period == 3)
    assert unverified_event.code == "U"
    assert unverified_event.severity == AttendanceCodeSeverity.P1_DIGEST
    assert unverified_event.notified is False


def test_retrospective_code_update_from_unexcused_to_excused():
    sentinel = AttendanceSentinel()

    # Previous P0 alert was notified
    existing_event = AttendanceEvent(
        date="2026-08-24",
        period=2,
        course_name="Algebra II",
        code="A",
        description="Unexcused Absence",
        severity=AttendanceCodeSeverity.P0_URGENT,
        notified=True,
        detected_at="2026-08-24T09:00:00+00:00",
    )

    # School office retrospectively changed 'A' to 'E' (Excused)
    records = [
        AttendanceRecordInput(
            date="2026-08-24",
            period=2,
            course_name="Algebra II",
            code="E",
            description="Excused by Parent",
        )
    ]

    alerts, updated_events = sentinel.evaluate_student_attendance(
        student_id="student_001",
        records=records,
        existing_events=[existing_event],
    )

    # No new alert should be sent
    assert len(alerts) == 0
    assert len(updated_events) == 1

    ev = updated_events[0]
    assert ev.code == "E"
    assert ev.severity == AttendanceCodeSeverity.IGNORED
    assert ev.description == "Excused by Parent"
