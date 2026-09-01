"""
Unit tests for Phase 3.1 Customizable Notification Thresholds and Grace Periods.
"""

import pytest
from datetime import datetime, timezone, timedelta
from src.storage.models import (
    StudentPreferences,
    StudentState,
    TrackedAssignment,
    LateSubmissionRecord,
    GradeSnapshot,
)
from src.storage.firestore import FirestoreStateEngine
from src.engine.authority import AsymmetricAuthorityEngine
from src.engine.models import CanvasAssignmentInput, StudentVelocityContext, CourseVelocityInput
from src.engine.velocity import GradeVelocityEngine
from src.engine.late_submissions import LateSubmissionSentinel
from src.radar.engine import WorkloadRadarEngine


def test_student_preferences_defaults_and_validation():
    """Verify default values and bounds validation for StudentPreferences."""
    prefs = StudentPreferences()
    assert prefs.grace_period_hours == 36
    assert prefs.velocity_drop_threshold == 4.0
    assert prefs.late_submission_threshold == 3
    assert prefs.workload_clumping_threshold == 2
    assert prefs.workload_clumping_window_hours == 48
    assert prefs.weekend_grace_pause is True

    # Custom valid values
    custom = StudentPreferences(
        grace_period_hours=24,
        velocity_drop_threshold=2.5,
        late_submission_threshold=2,
        workload_clumping_threshold=3,
        workload_clumping_window_hours=72,
        weekend_grace_pause=False,
    )
    assert custom.grace_period_hours == 24
    assert custom.velocity_drop_threshold == 2.5
    assert custom.late_submission_threshold == 2
    assert custom.workload_clumping_threshold == 3
    assert custom.workload_clumping_window_hours == 72
    assert custom.weekend_grace_pause is False

    # Out of bounds validation
    with pytest.raises(Exception):
        StudentPreferences(grace_period_hours=0)
    with pytest.raises(Exception):
        StudentPreferences(velocity_drop_threshold=0.1)


def test_authority_engine_custom_grace_period():
    """Verify AsymmetricAuthorityEngine respects custom grace_period_hours."""
    prefs = StudentPreferences(grace_period_hours=24, weekend_grace_pause=False)
    engine = AsymmetricAuthorityEngine(preferences=prefs)

    start_dt = datetime(2026, 9, 1, 10, 0, 0, tzinfo=timezone.utc)
    # 20 hours elapsed -> within 24h grace period
    eval_20h = start_dt + timedelta(hours=20)
    inp = CanvasAssignmentInput(
        assignment_id="101",
        course_id="MATH",
        title="Algebra Quiz",
        due_at=start_dt.isoformat(),
        submission_types=["online_upload"],
        is_missing=True,
    )

    tracked, alert = engine.evaluate_canvas_assignment(inp, existing_tracked=None, now=eval_20h)
    assert tracked.status == "GRACE_PERIOD"
    assert alert is None

    # 25 hours elapsed -> exceeds 24h grace period -> alert triggered
    eval_25h = start_dt + timedelta(hours=25)
    tracked_25, alert_25 = engine.evaluate_canvas_assignment(
        inp,
        existing_tracked=TrackedAssignment(
            title="Algebra Quiz",
            course_id="MATH",
            due_at=start_dt.isoformat(),
            submission_type="online_upload",
            status="GRACE_PERIOD",
            first_detected_missing=start_dt.isoformat(),
        ),
        now=eval_25h,
    )
    assert tracked_25.status == "EXPIRED"
    assert alert_25 is not None
    assert alert_25.assignment_id == "101"


def test_velocity_engine_custom_threshold():
    """Verify GradeVelocityEngine triggers alert based on custom velocity_drop_threshold."""
    # Standard threshold 4.0% vs custom threshold 2.5%
    prefs = StudentPreferences(velocity_drop_threshold=2.5)
    engine = GradeVelocityEngine(preferences=prefs)

    eval_date = datetime(2026, 9, 15, tzinfo=timezone.utc).date()
    tracking_start = "2026-09-01"

    history = [
        GradeSnapshot(date="2026-09-06", percentage=95.0, letter_grade="A"),
    ]

    context = StudentVelocityContext(
        student_id="student_1",
        tracking_start_date=tracking_start,
        courses=[
            CourseVelocityInput(
                course_id="HIST-101",
                course_name="US History",
                current_percentage=92.0,  # Drop = 3.0% (>= 2.5% custom threshold, < 4.0% standard)
                letter_grade="A-",
                history=history,
                total_graded_points=150.0,
                term_active_days=25,
            )
        ],
    )

    alerts = engine.evaluate_student_velocity(context, eval_date=eval_date)
    assert len(alerts) == 1
    assert alerts[0].course_id == "HIST-101"
    assert alerts[0].delta == 3.0


def test_late_submission_sentinel_custom_threshold():
    """Verify LateSubmissionSentinel triggers warning at custom frequency threshold."""
    prefs = StudentPreferences(late_submission_threshold=2)
    sentinel = LateSubmissionSentinel(preferences=prefs)

    now = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)
    records = [
        LateSubmissionRecord(
            assignment_id="1",
            course_id="ENG",
            title="Essay 1",
            submitted_at=(now - timedelta(days=1)).isoformat(),
            minutes_late=30,
            is_late=True,
        ),
        LateSubmissionRecord(
            assignment_id="2",
            course_id="ENG",
            title="Essay 2",
            submitted_at=(now - timedelta(days=2)).isoformat(),
            minutes_late=45,
            is_late=True,
        ),
    ]

    # With 2 late submissions and custom threshold=2, alert should be triggered
    alert, qualifying = sentinel.evaluate_late_submissions("student_1", records, now=now)
    assert alert is not None
    assert alert.count_in_window == 2
    assert len(qualifying) == 2


def test_workload_radar_engine_custom_clumping():
    """Verify WorkloadRadarEngine identifies clusters using custom count & window hours."""
    prefs = StudentPreferences(workload_clumping_threshold=3, workload_clumping_window_hours=72)
    engine = WorkloadRadarEngine(preferences=prefs)

    now = datetime(2026, 9, 1, 10, 0, 0, tzinfo=timezone.utc)
    assignments = [
        {
            "id": "1",
            "title": "Math Exam",
            "course_name": "Calculus",
            "due_at": (now + timedelta(hours=10)).isoformat(),
            "points_possible": 100,
        },
        {
            "id": "2",
            "title": "Physics Test",
            "course_name": "Physics",
            "due_at": (now + timedelta(hours=30)).isoformat(),
            "points_possible": 100,
        },
        {
            "id": "3",
            "title": "History Project",
            "course_name": "History",
            "due_at": (now + timedelta(hours=50)).isoformat(),
            "points_possible": 100,
        },
    ]

    # 3 assessments within 72h -> triggers clumping under custom threshold=3 & window=72h
    result = engine.evaluate(assignments, now=now)
    assert result.has_clumping is True
    assert len(result.clusters) == 1
    assert len(result.clusters[0].assessments) == 3


def test_firestore_preferences_persistence():
    """Verify FirestoreStateEngine stores and retrieves StudentPreferences correctly."""
    engine = FirestoreStateEngine(use_mock=True)
    student_id = "test_student_prefs"

    # Default fallback
    default_prefs = engine.get_student_preferences(student_id)
    assert default_prefs.grace_period_hours == 36

    # Update preferences
    custom_prefs = StudentPreferences(
        grace_period_hours=24,
        velocity_drop_threshold=3.0,
        late_submission_threshold=2,
    )
    engine.update_student_preferences(student_id, custom_prefs)

    # Retrieve updated preferences
    retrieved = engine.get_student_preferences(student_id)
    assert retrieved.grace_period_hours == 24
    assert retrieved.velocity_drop_threshold == 3.0
    assert retrieved.late_submission_threshold == 2
