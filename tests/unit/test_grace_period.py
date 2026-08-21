import pytest
from datetime import datetime, timedelta, timezone
from src.storage.models import TrackedAssignment, SubmissionType, AssignmentState
from src.engine.grace_period import GracePeriodEvaluator


def test_grace_period_entry_within_36h():
    evaluator = GracePeriodEvaluator(grace_period_hours=36.0)
    now = datetime.now(timezone.utc)
    assignment = TrackedAssignment(
        assignment_id="a1",
        course_id="c1",
        title="Physics Lab",
        submission_type=SubmissionType.ONLINE_UPLOAD,
        canvas_missing=True,
        powerschool_missing=False,
        state=AssignmentState.NEW
    )

    updated, should_alert = evaluator.evaluate(assignment, current_time=now)
    assert updated.state == AssignmentState.GRACE_PERIOD
    assert should_alert is False


def test_grace_period_expiration_post_36h():
    evaluator = GracePeriodEvaluator(grace_period_hours=36.0)
    now = datetime.now(timezone.utc)
    first_detected = now - timedelta(hours=37.0)

    assignment = TrackedAssignment(
        assignment_id="a1",
        course_id="c1",
        title="Physics Lab",
        submission_type=SubmissionType.ONLINE_UPLOAD,
        canvas_missing=True,
        powerschool_missing=False,
        state=AssignmentState.GRACE_PERIOD,
        first_detected_overdue=first_detected
    )

    updated, should_alert = evaluator.evaluate(assignment, current_time=now)
    assert updated.state == AssignmentState.ALERT_DISPATCHED
    assert should_alert is True


def test_grace_period_silent_resolution():
    evaluator = GracePeriodEvaluator(grace_period_hours=36.0)
    now = datetime.now(timezone.utc)

    assignment = TrackedAssignment(
        assignment_id="a1",
        course_id="c1",
        title="Physics Lab",
        submission_type=SubmissionType.ONLINE_UPLOAD,
        canvas_missing=False,  # Turned in!
        powerschool_missing=False,
        state=AssignmentState.GRACE_PERIOD,
        first_detected_overdue=now - timedelta(hours=10.0)
    )

    updated, should_alert = evaluator.evaluate(assignment, current_time=now)
    assert updated.state == AssignmentState.RESOLVED
    assert should_alert is False
