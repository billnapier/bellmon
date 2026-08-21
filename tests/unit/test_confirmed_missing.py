import pytest
from src.storage.models import TrackedAssignment, SubmissionType, AssignmentState
from src.engine.missing_work import MissingWorkEvaluator


def test_confirmed_missing_powerschool_flag():
    evaluator = MissingWorkEvaluator()
    assignment = TrackedAssignment(
        assignment_id="a2",
        course_id="c1",
        title="Math Homework",
        submission_type=SubmissionType.ONLINE_UPLOAD,
        canvas_missing=True,
        powerschool_missing=True,  # Explicitly marked missing in PowerSchool!
        state=AssignmentState.NEW
    )

    updated, should_alert, reason = evaluator.evaluate(assignment)
    assert should_alert is True
    assert updated.state == AssignmentState.ALERT_DISPATCHED
    assert reason == "CONFIRMED_POWERSCHOOL_MISSING"


def test_confirmed_missing_powerschool_zero_score():
    evaluator = MissingWorkEvaluator()
    assignment = TrackedAssignment(
        assignment_id="a3",
        course_id="c1",
        title="English Essay",
        submission_type=SubmissionType.ONLINE_UPLOAD,
        canvas_missing=True,
        powerschool_score=0.0,  # Score 0 entered in PowerSchool!
        state=AssignmentState.NEW
    )

    updated, should_alert, reason = evaluator.evaluate(assignment)
    assert should_alert is True
    assert updated.state == AssignmentState.ALERT_DISPATCHED
    assert reason == "CONFIRMED_POWERSCHOOL_ZERO"
