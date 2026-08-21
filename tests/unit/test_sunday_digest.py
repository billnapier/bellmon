import pytest
from datetime import datetime, timedelta, timezone
from src.storage.models import Student, CourseSnapshot, TrackedAssignment
from src.engine.clumping import WorkloadClumpingRadar
from src.router.email import EmailDigestRouter


def test_workload_clumping_detection():
    radar = WorkloadClumpingRadar(window_hours=48.0, min_assessments=2)
    now = datetime.now(timezone.utc)

    courses = [
        CourseSnapshot(
            course_id="c1",
            course_name="Chemistry Honors",
            teacher_name="Mr. Davis",
            current_score=91.0,
            grade_letter="A-",
            assignments=[
                TrackedAssignment(
                    assignment_id="exam_1",
                    course_id="c1",
                    title="Unit 3 Chemistry Exam",
                    due_at=now + timedelta(hours=12.0),
                    points_possible=100.0
                )
            ]
        ),
        CourseSnapshot(
            course_id="c2",
            course_name="AP US History",
            teacher_name="Mrs. Gable",
            current_score=88.0,
            grade_letter="B+",
            assignments=[
                TrackedAssignment(
                    assignment_id="proj_1",
                    course_id="c2",
                    title="DBQ Research Project",
                    due_at=now + timedelta(hours=36.0),
                    points_possible=75.0
                )
            ]
        )
    ]

    clusters = radar.scan(courses, now=now)
    assert len(clusters) == 2
    assert clusters[0]["title"] == "Unit 3 Chemistry Exam"


def test_sunday_digest_html_rendering():
    router = EmailDigestRouter()
    student = Student(
        student_id="s123",
        name="Alex Smith",
        courses=[
            CourseSnapshot(
                course_id="c1",
                course_name="Algebra II",
                teacher_name="Dr. Smith",
                current_score=95.0,
                grade_letter="A"
            )
        ]
    )

    clusters = [{"title": "Midterm Exam", "course_name": "Algebra II", "due_str": "Mon Aug 24 at 09:00 AM"}]
    html = router.render_sunday_digest(student, clusters)
    assert "Sunday Evening Workload Digest" in html
    assert "Alex Smith" in html
    assert "Workload Clumping Radar Warning" in html
