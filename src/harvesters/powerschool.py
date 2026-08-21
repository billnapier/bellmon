import httpx
from typing import List, Dict, Any, Tuple
from src.config import settings
from src.storage.models import CourseSnapshot, TrackedAssignment, AttendanceEvent


class PowerSchoolHarvester:
    def __init__(self, base_url: str = None, username: str = None, password: str = None):
        self.base_url = (base_url or settings.powerschool_base_url).rstrip("/")
        self.username = username or settings.powerschool_username
        self.password = password or settings.powerschool_password

    async def fetch_student_data(self, student_id: str) -> Tuple[List[CourseSnapshot], List[AttendanceEvent]]:
        """Fetch course grades and attendance records from PowerSchool."""
        if self.username.startswith("mock"):
            return self._get_mock_powerschool_data(student_id)

        # Real API call integration placeholder
        return [], []

    def _get_mock_powerschool_data(self, student_id: str) -> Tuple[List[CourseSnapshot], List[AttendanceEvent]]:
        courses = [
            CourseSnapshot(
                course_id="course_math_10",
                course_name="Algebra II Honors",
                teacher_name="Dr. Smith",
                current_score=92.5,
                grade_letter="A-",
                assignments=[
                    TrackedAssignment(
                        assignment_id="canvas_101",
                        course_id="course_math_10",
                        title="Chapter 4 Worksheet",
                        canvas_missing=True,
                        powerschool_missing=False,
                        powerschool_score=None,
                        powerschool_collected=False
                    )
                ]
            )
        ]
        attendance = [
            AttendanceEvent(
                event_id="att_001",
                student_id=student_id,
                date="2026-08-20",
                period="3",
                code="T",
                description="Tardy",
                is_unexcused=True
            )
        ]
        return courses, attendance
