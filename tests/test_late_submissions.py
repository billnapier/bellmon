"""
Unit and integration tests for Canvas Late Submission detection, LateSubmissionSentinel, and Sunday Digest rendering.
"""

from datetime import datetime, timezone, timedelta
import pytest

from src.ingestion.canvas import CanvasClient, CanvasSubmission
from src.engine.late_submissions import LateSubmissionSentinel
from src.engine.models import LateSubmissionPatternAlert
from src.storage.models import LateSubmissionRecord, DispatchedAlertRecord
from src.notifications.digest import SundayDigestPayload, SundayDigestRenderer


def test_harvest_canvas_late_submissions():
    """Test CanvasClient.process_late_submissions extracts LateSubmissionRecords accurately."""
    client = CanvasClient(token="test_token")
    submissions = [
        CanvasSubmission(
            assignment_id=101,
            course_id=1,
            submitted_at="2026-08-30T17:15:00Z",
            due_at="2026-08-30T17:00:00Z",
            late=True,
            seconds_late=900,
            assignment={"name": "Homework 1", "due_at": "2026-08-30T17:00:00Z"},
        ),
        CanvasSubmission(
            assignment_id=102,
            course_id=1,
            submitted_at="2026-08-30T16:50:00Z",
            due_at="2026-08-30T17:00:00Z",
            late=False,
            seconds_late=0,
            assignment={"name": "Homework 2 (On Time)", "due_at": "2026-08-30T17:00:00Z"},
        ),
        CanvasSubmission(
            assignment_id=103,
            course_id=2,
            submitted_at="2026-08-30T17:02:00Z",
            due_at="2026-08-30T17:00:00Z",
            late=True,
            seconds_late=120,
            assignment={"name": "Homework 3 (Slightly Late - 2 mins)", "due_at": "2026-08-30T17:00:00Z"},
        ),
    ]

    records = client.process_late_submissions("student_1", submissions, course_names={"1": "Math 101", "2": "English 101"})
    assert len(records) == 2  # Homework 1 and Homework 3 are late

    # Homework 1: 15 minutes late
    hw1 = next(r for r in records if r.assignment_id == "101")
    assert hw1.is_late is True
    assert hw1.minutes_late == 15
    assert hw1.title == "Homework 1"
    assert hw1.course_name == "Math 101"

    # Homework 3: 2 minutes late
    hw3 = next(r for r in records if r.assignment_id == "103")
    assert hw3.is_late is True
    assert hw3.minutes_late == 2
    assert hw3.course_name == "English 101"


def test_sentinel_below_threshold():
    """Test LateSubmissionSentinel triggers no alert if count is below threshold."""
    now = datetime(2026, 8, 31, 12, 0, tzinfo=timezone.utc)
    sentinel = LateSubmissionSentinel()

    # 2 qualifying late submissions (threshold is 3)
    records = [
        LateSubmissionRecord(
            student_id="student_1",
            assignment_id="1",
            title="Late 1",
            course_id="math",
            due_at=(now - timedelta(days=1, minutes=20)).isoformat(),
            submitted_at=(now - timedelta(days=1)).isoformat(),
            minutes_late=20,
            is_late=True,
            detected_at=now.isoformat(),
        ),
        LateSubmissionRecord(
            student_id="student_1",
            assignment_id="2",
            title="Late 2",
            course_id="math",
            due_at=(now - timedelta(days=2, minutes=10)).isoformat(),
            submitted_at=(now - timedelta(days=2)).isoformat(),
            minutes_late=10,
            is_late=True,
            detected_at=now.isoformat(),
        ),
        # 1 minor late submission (3 mins late, noise threshold < 5)
        LateSubmissionRecord(
            student_id="student_1",
            assignment_id="3",
            title="Minor Late",
            course_id="math",
            due_at=(now - timedelta(days=3, minutes=3)).isoformat(),
            submitted_at=(now - timedelta(days=3)).isoformat(),
            minutes_late=3,
            is_late=True,
            detected_at=now.isoformat(),
        ),
    ]

    alert, qualifying = sentinel.evaluate_late_submissions("student_1", records, now=now)
    assert alert is None
    assert len(qualifying) == 2


def test_sentinel_triggers_p1_alert():
    """Test LateSubmissionSentinel triggers P1 alert when threshold is reached."""
    now = datetime(2026, 8, 31, 12, 0, tzinfo=timezone.utc)
    sentinel = LateSubmissionSentinel()

    records = [
        LateSubmissionRecord(
            student_id="student_1",
            assignment_id=f"a_{i}",
            title=f"Late Assignment {i}",
            course_id="math",
            due_at=(now - timedelta(days=i, minutes=15)).isoformat(),
            submitted_at=(now - timedelta(days=i)).isoformat(),
            minutes_late=15,
            is_late=True,
            detected_at=now.isoformat(),
        )
        for i in range(1, 4)
    ]

    alert, qualifying = sentinel.evaluate_late_submissions("student_1", records, now=now)
    assert alert is not None
    assert isinstance(alert, LateSubmissionPatternAlert)
    assert alert.severity == "P1_WARNING"
    assert alert.count_in_window == 3
    assert len(qualifying) == 3


def test_sentinel_cooldown():
    """Test LateSubmissionSentinel respects 7-day cooldown window."""
    now = datetime(2026, 8, 31, 12, 0, tzinfo=timezone.utc)
    sentinel = LateSubmissionSentinel()

    records = [
        LateSubmissionRecord(
            student_id="student_1",
            assignment_id=f"a_{i}",
            title=f"Late Assignment {i}",
            course_id="math",
            due_at=(now - timedelta(days=i, minutes=15)).isoformat(),
            submitted_at=(now - timedelta(days=i)).isoformat(),
            minutes_late=15,
            is_late=True,
            detected_at=now.isoformat(),
        )
        for i in range(1, 4)
    ]

    dispatched_alerts = [
        DispatchedAlertRecord(
            alert_id="alert_prev",
            student_id="student_1",
            alert_type="LATE_SUBMISSION_FREQUENCY_WARNING",
            severity="P1_WARNING",
            channel="email",
            dispatched_at=(now - timedelta(days=3)).isoformat(),
        )
    ]

    # Cooldown active -> Alert should be suppressed, but qualifying records returned
    alert, qualifying = sentinel.evaluate_late_submissions(
        "student_1", records, now=now, dispatched_alerts=dispatched_alerts
    )
    assert alert is None
    assert len(qualifying) == 3

    # Older alert outside 7-day cooldown -> Alert should trigger
    old_dispatched_alerts = [
        DispatchedAlertRecord(
            alert_id="alert_old",
            student_id="student_1",
            alert_type="LATE_SUBMISSION_FREQUENCY_WARNING",
            severity="P1_WARNING",
            channel="email",
            dispatched_at=(now - timedelta(days=8)).isoformat(),
        )
    ]
    alert2, qualifying2 = sentinel.evaluate_late_submissions(
        "student_1", records, now=now, dispatched_alerts=old_dispatched_alerts
    )
    assert alert2 is not None
    assert alert2.count_in_window == 3


def test_sunday_digest_rendering_with_late_submissions():
    """Test SundayDigestRenderer includes late submissions and warning banner."""
    renderer = SundayDigestRenderer()

    # Case 1: No late submissions
    payload_clean = SundayDigestPayload(
        student_name="Alice",
        late_submissions=[],
        late_count=0,
        has_late_warning=False,
    )
    html_clean = renderer.render_html(payload_clean)
    text_clean = renderer.render_text(payload_clean)

    assert "CHRONIC LATE SUBMISSION WARNING" not in html_clean
    assert "No late submissions recorded in the past 7 days." in html_clean
    assert "No late submissions recorded in the past 7 days." in text_clean

    # Case 2: With late submissions & warning
    late_recs = [
        {"course_name": "Math 101", "assignment_name": "Quiz 1", "minutes_late": 45, "submitted_at": "2026-08-29T18:45:00Z"},
        {"course_name": "Physics", "assignment_name": "Lab 2", "minutes_late": 120, "submitted_at": "2026-08-30T20:00:00Z"},
        {"course_name": "History", "assignment_name": "Essay 1", "minutes_late": 15, "submitted_at": "2026-08-31T09:15:00Z"},
    ]
    payload_warn = SundayDigestPayload(
        student_name="Alice",
        late_submissions=late_recs,
        late_count=3,
        has_late_warning=True,
    )

    html_warn = renderer.render_html(payload_warn)
    text_warn = renderer.render_text(payload_warn)

    assert "CHRONIC LATE SUBMISSION WARNING" in html_warn
    assert "Student submitted 3 assignments late in the past 7 days." in html_warn
    assert "Quiz 1" in html_warn
    assert "45 mins" in html_warn

    assert "*** CHRONIC LATE SUBMISSION WARNING: Student submitted 3 assignments late in the past 7 days. ***" in text_warn
    assert "Quiz 1: 45 mins late" in text_warn
