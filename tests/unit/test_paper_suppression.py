import pytest
from src.storage.models import TrackedAssignment, SubmissionType, AssignmentState
from src.engine.missing_work import MissingWorkEvaluator


def test_paper_work_suppressed_when_score_exists():
    evaluator = MissingWorkEvaluator()
    assignment = TrackedAssignment(
        assignment_id="a4",
        course_id="c1",
        title="History Paper Worksheet",
        submission_type=SubmissionType.PAPER,
        canvas_missing=True,  # Canvas flagged missing because not uploaded online
        powerschool_score=45.0,  # Graded in PowerSchool (45/50)
        state=AssignmentState.NEW
    )

    updated, should_alert, reason = evaluator.evaluate(assignment)
    assert should_alert is False
    assert updated.state == AssignmentState.SUPPRESSED_PAPER_OR_GRADED
    assert reason == "SUPPRESSED_PAPER_OR_GRADED"


def test_paper_work_suppressed_when_collected_flag_true():
    evaluator = MissingWorkEvaluator()
    assignment = TrackedAssignment(
        assignment_id="a5",
        course_id="c1",
        title="Biology Handout",
        submission_type=SubmissionType.PAPER,
        canvas_missing=True,
        powerschool_collected=True,  # Handed in physical copy
        state=AssignmentState.NEW
    )

    updated, should_alert, reason = evaluator.evaluate(assignment)
    assert should_alert is False
    assert updated.state == AssignmentState.SUPPRESSED_PAPER_OR_GRADED
    assert reason == "SUPPRESSED_PAPER_OR_GRADED"
