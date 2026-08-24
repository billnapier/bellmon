"""
Unit tests for GradeVelocityEngine (Phase 1.3).
"""

from datetime import date, timedelta
import pytest
from src.engine.models import (
    CourseVelocityInput,
    PendingGradeDropAlert,
    StudentVelocityContext,
)
from src.engine.velocity import GradeVelocityEngine
from src.storage.models import GradeSnapshot


@pytest.fixture
def engine():
    return GradeVelocityEngine()


def test_user_story_1_rolling_grade_drop_detection(engine):
    """
    User Story 1: Given a current grade of 88.0% and a 7-day snapshot of 93.0%,
    triggers PendingGradeDropAlert with delta 5.0%.
    Given current 91.0% and snapshot 93.5% (delta 2.5%), triggers no alert.
    """
    eval_d = date(2026, 8, 20)
    snap_date = (eval_d - timedelta(days=7)).isoformat()

    context = StudentVelocityContext(
        student_id="student_1",
        tracking_start_date="2026-08-01",  # > 7 days prior
        courses=[
            CourseVelocityInput(
                course_id="alg2",
                course_name="Algebra II",
                current_percentage=88.0,
                total_graded_points=150.0,
                term_active_days=25,
                history=[
                    GradeSnapshot(date=snap_date, percentage=93.0, letter_grade="A")
                ],
            ),
            CourseVelocityInput(
                course_id="eng10",
                course_name="English 10",
                current_percentage=91.0,
                total_graded_points=150.0,
                term_active_days=25,
                history=[
                    GradeSnapshot(date=snap_date, percentage=93.5, letter_grade="A")
                ],
            ),
        ],
    )

    alerts = engine.evaluate_student_velocity(context, eval_date=eval_d)

    assert len(alerts) == 1
    assert alerts[0].course_id == "alg2"
    assert alerts[0].course_name == "Algebra II"
    assert alerts[0].prev_percentage == 93.0
    assert alerts[0].curr_percentage == 88.0
    assert alerts[0].delta == 5.0


def test_user_story_2_early_term_noise_suppression(engine):
    """
    User Story 2: Grade drop >= 4.0% in course with < 100 total points AND < 21 term days
    is suppressed. When total points >= 100 OR term days >= 21, alert is generated.
    """
    eval_d = date(2026, 8, 20)
    snap_date = (eval_d - timedelta(days=7)).isoformat()

    context = StudentVelocityContext(
        student_id="student_1",
        tracking_start_date="2026-08-01",
        courses=[
            # Suppressed: < 100 points AND < 21 term days
            CourseVelocityInput(
                course_id="suppressed_course",
                course_name="Volatile Intro Course",
                current_percentage=80.0,
                total_graded_points=40.0,
                term_active_days=14,
                history=[
                    GradeSnapshot(date=snap_date, percentage=90.0, letter_grade="A")
                ],
            ),
            # Alerted: points >= 100 even if term days < 21
            CourseVelocityInput(
                course_id="points_sufficient",
                course_name="AP Physics",
                current_percentage=80.0,
                total_graded_points=150.0,
                term_active_days=14,
                history=[
                    GradeSnapshot(date=snap_date, percentage=90.0, letter_grade="A")
                ],
            ),
            # Alerted: term days >= 21 even if points < 100
            CourseVelocityInput(
                course_id="days_sufficient",
                course_name="US History",
                current_percentage=80.0,
                total_graded_points=40.0,
                term_active_days=25,
                history=[
                    GradeSnapshot(date=snap_date, percentage=90.0, letter_grade="A")
                ],
            ),
        ],
    )

    alerts = engine.evaluate_student_velocity(context, eval_date=eval_d)

    triggered_ids = {a.course_id for a in alerts}
    assert "suppressed_course" not in triggered_ids
    assert "points_sufficient" in triggered_ids
    assert "days_sufficient" in triggered_ids


def test_user_story_3_silent_warming_protocol(engine):
    """
    User Story 3: Student tracking history < 7 calendar days suppresses all velocity drop alerts.
    """
    eval_d = date(2026, 8, 20)

    # Student registered 3 days ago
    recent_context = StudentVelocityContext(
        student_id="new_student",
        tracking_start_date="2026-08-17",
        courses=[
            CourseVelocityInput(
                course_id="chem",
                course_name="Chemistry",
                current_percentage=75.0,
                total_graded_points=200.0,
                term_active_days=30,
                history=[
                    GradeSnapshot(date="2026-08-10", percentage=95.0, letter_grade="A")
                ],
            )
        ],
    )

    alerts = engine.evaluate_student_velocity(recent_context, eval_date=eval_d)
    assert len(alerts) == 0


def test_baseline_snapshot_selection_target_and_fallback(engine):
    """
    Tests snapshot selection:
    1. Snapshot in [t-10, t-7] target window selected.
    2. Snapshot in [t-14, t-7] fallback window selected if target missing.
    3. Deferred if no snapshot >= 7 days prior.
    """
    eval_d = date(2026, 8, 20)

    # Target window test
    h_target = [
        GradeSnapshot(date="2026-08-13", percentage=95.0, letter_grade="A"),  # 7 days ago
        GradeSnapshot(date="2026-08-11", percentage=92.0, letter_grade="A"),  # 9 days ago
        GradeSnapshot(date="2026-08-05", percentage=88.0, letter_grade="B"),  # 15 days ago
    ]
    target_snap = engine.find_baseline_snapshot(h_target, eval_d)
    assert target_snap is not None
    assert target_snap.percentage == 95.0  # Most recent in target window

    # Fallback window test (no snapshot in t-10..t-7, snapshot in t-12)
    h_fallback = [
        GradeSnapshot(date="2026-08-08", percentage=94.0, letter_grade="A"),  # 12 days ago
        GradeSnapshot(date="2026-08-05", percentage=88.0, letter_grade="B"),  # 15 days ago
    ]
    fallback_snap = engine.find_baseline_snapshot(h_fallback, eval_d)
    assert fallback_snap is not None
    assert fallback_snap.percentage == 94.0

    # Deferred test (snapshots only 3 days ago or 16 days ago)
    h_deferred = [
        GradeSnapshot(date="2026-08-18", percentage=90.0, letter_grade="A"),  # 2 days ago
        GradeSnapshot(date="2026-08-01", percentage=90.0, letter_grade="A"),  # 19 days ago
    ]
    deferred_snap = engine.find_baseline_snapshot(h_deferred, eval_d)
    assert deferred_snap is None
