import pytest
from src.storage.models import CourseSnapshot, TrackedAssignment
from src.engine.velocity import VelocityDropEvaluator


def test_velocity_drop_warning_triggered():
    evaluator = VelocityDropEvaluator(threshold=4.0)

    historical = CourseSnapshot(
        course_id="c1",
        course_name="Algebra II",
        teacher_name="Dr. Smith",
        current_score=94.0,  # 7 days ago
        grade_letter="A"
    )

    current = CourseSnapshot(
        course_id="c1",
        course_name="Algebra II",
        teacher_name="Dr. Smith",
        current_score=89.0,  # Drop of 5.0% (>= 4.0%)
        grade_letter="B+",
        assignments=[
            TrackedAssignment(
                assignment_id="a10",
                course_id="c1",
                title="Midterm Exam",
                powerschool_score=60.0,
                points_possible=100.0
            )
        ]
    )

    should_alert, drop, impacting = evaluator.evaluate(historical, current)
    assert should_alert is True
    assert drop == 5.0
    assert impacting is not None
    assert impacting.title == "Midterm Exam"


def test_velocity_drop_below_threshold():
    evaluator = VelocityDropEvaluator(threshold=4.0)

    historical = CourseSnapshot(
        course_id="c1",
        course_name="Algebra II",
        teacher_name="Dr. Smith",
        current_score=94.0,
        grade_letter="A"
    )

    current = CourseSnapshot(
        course_id="c1",
        course_name="Algebra II",
        teacher_name="Dr. Smith",
        current_score=92.0,  # Drop of 2.0% (< 4.0%)
        grade_letter="A-"
    )

    should_alert, drop, impacting = evaluator.evaluate(historical, current)
    assert should_alert is False
    assert drop == 2.0
