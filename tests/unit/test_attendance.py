import pytest
from src.storage.models import AttendanceEvent
from src.engine.attendance import AttendanceEvaluator


def test_unexcused_attendance_anomaly():
    evaluator = AttendanceEvaluator()
    event = AttendanceEvent(
        event_id="e1",
        student_id="s1",
        date="2026-08-20",
        period="2",
        code="CUT",
        description="Unexcused Cut",
        is_unexcused=True
    )

    should_alert, title, msg = evaluator.evaluate(event)
    assert should_alert is True
    assert "Attendance Anomaly" in title
    assert "Unexcused Cut" in msg


def test_excused_attendance_no_alert():
    evaluator = AttendanceEvaluator()
    event = AttendanceEvent(
        event_id="e2",
        student_id="s1",
        date="2026-08-20",
        period="1",
        code="MED",
        description="Medical Excused",
        is_unexcused=False
    )

    should_alert, title, msg = evaluator.evaluate(event)
    assert should_alert is False
