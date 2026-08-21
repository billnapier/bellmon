from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from src.config import settings
from src.storage.models import CourseSnapshot, TrackedAssignment


class WorkloadClumpingRadar:
    def __init__(self, window_hours: float = None, min_assessments: int = None):
        self.window_hours = window_hours or settings.workload_clumping_window_hours
        self.min_assessments = min_assessments or settings.workload_clumping_min_assessments

    def scan(
        self,
        courses: List[CourseSnapshot],
        now: datetime = None
    ) -> List[Dict[str, Any]]:
        """
        Scans for workload clumping (>= 2 major assessments due in a 48h window).
        Returns list of clumping assessment dictionaries for digest rendering.
        """
        current_time = now or datetime.now(timezone.utc)
        window_end = current_time + timedelta(hours=self.window_hours)

        upcoming_major = []
        for course in courses:
            for assignment in course.assignments:
                if assignment.due_at and current_time <= assignment.due_at <= window_end:
                    # Major assessment heuristic: points >= 50 or title contains Exam/Project/Midterm
                    is_major = (
                        assignment.points_possible >= 50.0
                        or any(kw in assignment.title.lower() for kw in ["exam", "test", "project", "midterm", "quiz"])
                    )
                    if is_major:
                        upcoming_major.append({
                            "title": assignment.title,
                            "course_name": course.course_name,
                            "due_str": assignment.due_at.strftime("%a %b %d at %I:%M %p")
                        })

        if len(upcoming_major) >= self.min_assessments:
            return upcoming_major
        return []
