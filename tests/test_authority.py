"""
Unit tests for Asymmetric System Authority & 36-Hour Grace Period Evaluation Engine.
"""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import pytest

from src.storage.models import TrackedAssignment
from src.engine.models import (
    AssignmentStatus,
    AlertSource,
    CanvasAssignmentInput,
    PowerSchoolAssignmentInput,
    PendingMissingAlert,
)
from src.engine.authority import AsymmetricAuthorityEngine, is_weekend_blackout


@pytest.fixture
def engine():
    return AsymmetricAuthorityEngine(grace_period_hours=36.0, timezone_str="America/Los_Angeles")


def test_weekend_blackout_detection():
    tz = ZoneInfo("America/Los_Angeles")
    # Friday 4:59 PM - Not blackout
    dt_fri_4pm = datetime(2026, 8, 28, 16, 59, 0, tzinfo=tz)
    assert not is_weekend_blackout(dt_fri_4pm)

    # Friday 5:00 PM - Blackout starts
    dt_fri_5pm = datetime(2026, 8, 28, 17, 0, 0, tzinfo=tz)
    assert is_weekend_blackout(dt_fri_5pm)

    # Saturday 12:00 PM - Blackout
    dt_sat = datetime(2026, 8, 29, 12, 0, 0, tzinfo=tz)
    assert is_weekend_blackout(dt_sat)

    # Sunday 11:59 PM - Blackout
    dt_sun = datetime(2026, 8, 30, 23, 59, 0, tzinfo=tz)
    assert is_weekend_blackout(dt_sun)

    # Monday 7:59 AM - Blackout
    dt_mon_759am = datetime(2026, 8, 31, 7, 59, 0, tzinfo=tz)
    assert is_weekend_blackout(dt_mon_759am)

    # Monday 8:00 AM - Blackout ends
    dt_mon_8am = datetime(2026, 8, 31, 8, 0, 0, tzinfo=tz)
    assert not is_weekend_blackout(dt_mon_8am)


def test_calculate_weekday_elapsed_hours_pure_weekday(engine):
    tz = ZoneInfo("America/Los_Angeles")
    # Monday 9:00 AM to Monday 5:00 PM -> 8 active hours
    start_dt = datetime(2026, 8, 24, 9, 0, 0, tzinfo=tz)
    end_dt = datetime(2026, 8, 24, 17, 0, 0, tzinfo=tz)
    elapsed = engine.calculate_weekday_elapsed_hours(start_dt, end_dt)
    assert abs(elapsed - 8.0) < 0.05


def test_calculate_weekday_elapsed_hours_weekend_pause(engine):
    tz = ZoneInfo("America/Los_Angeles")
    # Friday 5:00 PM (blackout starts) to Monday 8:00 AM (blackout ends)
    # Total wall-clock duration is 63 hours, but active weekday duration must be 0!
    start_dt = datetime(2026, 8, 28, 17, 0, 0, tzinfo=tz)
    end_dt = datetime(2026, 8, 31, 8, 0, 0, tzinfo=tz)
    elapsed = engine.calculate_weekday_elapsed_hours(start_dt, end_dt)
    assert abs(elapsed - 0.0) < 0.05


def test_canvas_digital_missing_initialization(engine):
    tz = ZoneInfo("America/Los_Angeles")
    now = datetime(2026, 8, 24, 10, 0, 0, tzinfo=tz)

    canvas_item = CanvasAssignmentInput(
        assignment_id="c_101",
        title="Essay 1",
        course_id="eng_9",
        due_at=now.isoformat(),
        submission_types=["online_upload"],
        is_missing=True,
    )

    tracked, alert = engine.evaluate_canvas_assignment(canvas_item, existing_tracked=None, now=now)

    assert tracked.status == AssignmentStatus.GRACE_PERIOD.value
    assert tracked.first_detected_missing == now.isoformat()
    assert alert is None


def test_canvas_digital_missing_grace_period_expiration(engine):
    tz = ZoneInfo("America/Los_Angeles")
    start_dt = datetime(2026, 8, 24, 8, 0, 0, tzinfo=tz)  # Monday 8:00 AM

    canvas_item = CanvasAssignmentInput(
        assignment_id="c_102",
        title="Math HW 1",
        course_id="math_10",
        due_at=start_dt.isoformat(),
        submission_types=["online_upload"],
        is_missing=True,
    )

    existing_tracked = TrackedAssignment(
        title="Math HW 1",
        course_id="math_10",
        due_at=start_dt.isoformat(),
        submission_type="online_upload",
        status=AssignmentStatus.GRACE_PERIOD.value,
        first_detected_missing=start_dt.isoformat(),
        alert_dispatched=False,
    )

    # 35 active hours later (Tuesday 7:00 PM) -> Still GRACE_PERIOD
    now_35h = start_dt + timedelta(hours=35)
    tracked_35h, alert_35h = engine.evaluate_canvas_assignment(canvas_item, existing_tracked, now=now_35h)
    assert tracked_35h.status == AssignmentStatus.GRACE_PERIOD.value
    assert alert_35h is None

    # 36.5 active hours later (Tuesday 8:30 PM) -> EXPIRED + Alert
    now_36h = start_dt + timedelta(hours=36, minutes=30)
    tracked_36h, alert_36h = engine.evaluate_canvas_assignment(canvas_item, existing_tracked, now=now_36h)
    assert tracked_36h.status == AssignmentStatus.EXPIRED.value
    assert alert_36h is not None
    assert alert_36h.source == AlertSource.CANVAS_GRACE_EXPIRED
    assert alert_36h.assignment_id == "c_102"


def test_canvas_digital_missing_submitted_resolution(engine):
    tz = ZoneInfo("America/Los_Angeles")
    now = datetime(2026, 8, 24, 14, 0, 0, tzinfo=tz)

    canvas_item = CanvasAssignmentInput(
        assignment_id="c_103",
        title="Lab Report",
        course_id="sci_9",
        due_at=now.isoformat(),
        submission_types=["online_upload"],
        is_missing=False,  # Student submitted!
    )

    existing_tracked = TrackedAssignment(
        title="Lab Report",
        course_id="sci_9",
        due_at=now.isoformat(),
        submission_type="online_upload",
        status=AssignmentStatus.GRACE_PERIOD.value,
        first_detected_missing=now.isoformat(),
        alert_dispatched=False,
    )

    tracked, alert = engine.evaluate_canvas_assignment(canvas_item, existing_tracked, now=now)
    assert tracked.status == AssignmentStatus.RESOLVED.value
    assert alert is None


def test_canvas_paper_work_suppression(engine):
    tz = ZoneInfo("America/Los_Angeles")
    now = datetime(2026, 8, 24, 10, 0, 0, tzinfo=tz)

    canvas_item = CanvasAssignmentInput(
        assignment_id="c_104",
        title="Physical Worksheet",
        course_id="hist_10",
        due_at=now.isoformat(),
        submission_types=["on_paper"],
        is_missing=True,
    )

    tracked, alert = engine.evaluate_canvas_assignment(canvas_item, existing_tracked=None, now=now)
    assert tracked.status == AssignmentStatus.SUPPRESSED.value
    assert alert is None


def test_powerschool_confirmed_missing_alert(engine):
    tz = ZoneInfo("America/Los_Angeles")
    now = datetime(2026, 8, 24, 10, 0, 0, tzinfo=tz)

    # PowerSchool item with is_missing: True
    ps_item_missing = PowerSchoolAssignmentInput(
        assignment_id="ps_201",
        title="Quiz 1",
        course_id="math_10",
        due_at=now.isoformat(),
        is_missing=True,
        score=None,
        points_possible=100.0,
    )

    tracked, alert = engine.evaluate_powerschool_assignment(ps_item_missing, existing_tracked=None, now=now)
    assert tracked.status == AssignmentStatus.CONFIRMED_MISSING.value
    assert alert is not None
    assert alert.source == AlertSource.POWERSCHOOL_CONFIRMED
    assert alert.assignment_id == "ps_201"
    assert alert.points_possible == 100.0

    # PowerSchool item with score: 0
    ps_item_zero = PowerSchoolAssignmentInput(
        assignment_id="ps_202",
        title="Project Draft",
        course_id="eng_9",
        due_at=now.isoformat(),
        is_missing=False,
        score=0.0,
        points_possible=50.0,
    )

    tracked_zero, alert_zero = engine.evaluate_powerschool_assignment(ps_item_zero, existing_tracked=None, now=now)
    assert tracked_zero.status == AssignmentStatus.CONFIRMED_MISSING.value
    assert alert_zero is not None
    assert alert_zero.source == AlertSource.POWERSCHOOL_CONFIRMED


def test_powerschool_duplicate_alert_suppression(engine):
    tz = ZoneInfo("America/Los_Angeles")
    now = datetime(2026, 8, 24, 10, 0, 0, tzinfo=tz)

    ps_item = PowerSchoolAssignmentInput(
        assignment_id="ps_201",
        title="Quiz 1",
        course_id="math_10",
        due_at=now.isoformat(),
        is_missing=True,
        score=None,
        points_possible=100.0,
    )

    existing_tracked = TrackedAssignment(
        title="Quiz 1",
        course_id="math_10",
        due_at=now.isoformat(),
        submission_type="powerschool_gradebook",
        status=AssignmentStatus.CONFIRMED_MISSING.value,
        first_detected_missing=now.isoformat(),
        alert_dispatched=True,
    )

    tracked, alert = engine.evaluate_powerschool_assignment(ps_item, existing_tracked=existing_tracked, now=now)
    assert tracked.status == AssignmentStatus.CONFIRMED_MISSING.value
    assert alert is None  # Already dispatched alert is suppressed on subsequent runs
